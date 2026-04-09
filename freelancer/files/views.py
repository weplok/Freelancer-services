from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import uuid


def homepage(request):
    return render(request, "files/index.html")


def test_ui(request):
    return render(request, "files/test_ui.html")


def upload_file(request):
    if request.method == 'POST':
        file = request.FILES.get('file')

        if not file:
            return JsonResponse({'error': 'Нет файла'}, status=400)

        filename = f"{uuid.uuid4()}_{file.name}"

        with open(f'media/{filename}', 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        return JsonResponse({'status': 'ok', 'filename': file.name})

    return render(request, "files/upload_file.html")
