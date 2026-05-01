from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from .models import Detection
from .predictor import predictor
from django.conf import settings
import os
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def home(request):
    if request.user.is_authenticated:
        latest_detections = Detection.objects.filter(user=request.user).order_by('-created_at')[:5]
    else:
        latest_detections = []
    return render(request, 'detection/home.html', {'latest_detections': latest_detections})

@login_required
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        detection = Detection.objects.create(image=image, user=request.user)
        
        # Run prediction
        result = predictor.predict(detection.image.path)
        
        # Store structured results
        detection.crop_type = result['crop_disease'].split(' - ')[0]
        detection.disease = result['crop_disease'].split(' - ')[1]
        detection.confidence = result['confidence']
        detection.treatment = result['treatment']
        detection.prevention = result['prevention']
        detection.care_tips = result['care_tips']
        detection.save()
        
        return redirect('results', pk=detection.pk)
    
    return render(request, 'detection/upload.html')

@login_required
def results(request, pk):
    detection = get_object_or_404(Detection, pk=pk, user=request.user)
    return render(request, 'detection/results.html', {'detection': detection})

@login_required
def history(request):
    detections = Detection.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'detection/history.html', {'detections': detections})

@login_required
def download_report_pdf(request, pk):
    detection = get_object_or_404(Detection, pk=pk, user=request.user)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="report_{pk}.pdf"'
    
    p = canvas.Canvas(response, pagesize=letter)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "Crop Detection Report")
    p.setFont("Helvetica", 12)
    p.drawString(100, 730, f"Date: {detection.created_at.strftime('%Y-%m-%d %H:%M')}")
    p.drawString(100, 710, f"Crop Type: {detection.crop_type}")
    p.drawString(100, 690, f"Disease: {detection.disease}")
    p.drawString(100, 670, f"Confidence: {detection.confidence}%")
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, 640, "Treatment Plan:")
    p.setFont("Helvetica", 10)
    p.drawString(100, 625, detection.treatment[:100]) # Simple truncation for now
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, 600, "Prevention Strategies:")
    p.setFont("Helvetica", 10)
    p.drawString(100, 585, detection.prevention[:100])
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, 560, "Ongoing Care Tips:")
    p.setFont("Helvetica", 10)
    p.drawString(100, 545, detection.care_tips[:100])
    
    p.showPage()
    p.save()
    return response

@login_required
def export_csv(request):
    detections = Detection.objects.filter(user=request.user).values('crop_type', 'disease', 'confidence', 'created_at')
    df = pd.DataFrame(list(detections))
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="detections_history.csv"'
    df.to_csv(path_or_buf=response, index=False)
    return response

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account has been created.")
            return redirect('home')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
