from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import ImageCreateForm

IMAGE_SAVE_MESSAGE = 'Изображение сохранено.'


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
            messages.success(request, IMAGE_SAVE_MESSAGE)
            return redirect(new_image.get_absolute_url())
    return render(
        request,
        'images/image/create.html',
        {'section': 'images', 'form': form}
    )


