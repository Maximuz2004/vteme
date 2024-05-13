from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, Paginator, PageNotAnInteger
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

import redis

from actions.utils import create_action
from .forms import ImageCreateForm
from .models import Image

IMAGE_SAVE_MESSAGE = 'Изображение добавлено в закладки'
LIKES_MESSAGE = 'Понравилось'
STATUS_OK = {'status': 'ok'}
STATUS_ERROR = {'status': 'error'}

redis_conn = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

@login_required
def image_create(request):
    form = ImageCreateForm(data=request.GET)
    if request.method == 'POST':
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            new_image = form.save(commit=False)
            new_image.user = request.user
            new_image.save()
            create_action(request.user, IMAGE_SAVE_MESSAGE, new_image)
            messages.success(request, IMAGE_SAVE_MESSAGE)
            return redirect(new_image.get_absolute_url())
    return render(
        request,
        'images/image/create.html',
        {'section': 'images', 'form': form}
    )


def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    total_views = redis_conn.incr(f'image:{image.id}:views')
    redis_conn.zincrby('image_ranking', 1, image.id)
    return render(
        request,
        'images/image/detail.html',
        {
            'section': 'images',
            'image': image,
            'total_views': total_views
        }
    )


@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, LIKES_MESSAGE, image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse(STATUS_OK)
        except Image.DoesNotExist:
            pass
        return JsonResponse(STATUS_ERROR)


@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 9)
    page = request.GET.get('page')
    images_only = request.GET.get('images_only')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        if images_only:
            return HttpResponse('')
        images = paginator.page(paginator.num_pages)
    if images_only:
        return render(
            request,
            'images/image/list_images.html',
            {'section': 'images', 'images': images}
        )
    return render(
        request,
        'images/image/list.html',
        {'section': 'images', 'images': images}
    )

@login_required
def image_ranking(request):
    image_ranks = redis_conn.zrange(
        'image_ranking',
        0,
        -1,
        desc=True
    )[:10]
    image_ranking_ids = [int(id) for id in image_ranks]
    most_viewed_images = list(
        Image.objects.filter(id__in=image_ranking_ids)
    )
    most_viewed_images.sort(key=lambda x: image_ranking_ids.index(x.id))
    return render(
        request,
        'images/image/ranking.html',
        {'section': 'images', 'most_viewed': most_viewed_images}
    )
