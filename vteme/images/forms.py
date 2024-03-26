from django import forms
from django.core.exceptions import BadRequest
from django.core.files.base import ContentFile
from django.utils.text import slugify
import requests

from .models import Image

VALID_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png']
IMAGE_EXT_VALIDATION_ERROR = 'Данный URL не содержит валидную картинку'
REQUEST_IMAGE_ERROR = 'Произошла ошибка при загрузке изображения: {}'
REQUEST_UNKNOWN_ERROR = 'Произошла неизвестная ошибкаЖ {}'


class ImageCreateForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['title', 'url', 'description']
        widgets = {
            'url': forms.HiddenInput,

        }

    def clean_url(self):
        url = self.cleaned_data['url']
        extension = url.rsplit('.', 1)[1].lower()
        if extension not in VALID_IMAGE_EXTENSIONS:
            raise forms.ValidationError(IMAGE_EXT_VALIDATION_ERROR)
        return url

    def save(self, force_insert=False, force_update=False, commit=True):
        image = super().save(commit=False)
        image_url = self.cleaned_data['url']
        name = slugify(image.title)
        extension = image_url.rsplit('.', 1)[1].lower()
        image_name = f'{name}.{extension}'
        try:
            response = requests.get(image_url)
            image.image.save(
                image_name,
                ContentFile(response.content),
                save=False
            )
        except requests.exceptions.RequestException as e:
            print(REQUEST_IMAGE_ERROR.format(e))
        except Exception as e:
            print(REQUEST_UNKNOWN_ERROR.format(e))
        if commit:
            image.save()
        return image
