from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, Paginator, PageNotAnInteger
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from actions.utils import create_action
from .forms import ImageCreateForm
from .models import Image

IMAGE_SAVE_MESSAGE = 'Изображение добавлено в закладки'
STATUS_OK = {'status': 'ok'}
STATUS_ERROR = {'status': 'error'}


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
    return render(
        request,
        'images/image/detail.html',
        {'section': 'images', 'image': image}
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