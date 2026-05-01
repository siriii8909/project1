import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cropdetect.settings')
django.setup()

from detection.models import Detection
from django.contrib.auth.models import User
from django.core.files.base import ContentFile

def verify():
    print("Starting verification...")
    
    # 1. Get or create admin user
    user = User.objects.get(username='admin')
    
    # 2. Create a dummy detection record
    # Note: We use a ContentFile to simulate an image upload
    test_image = ContentFile(b"dummy image data", name="test_supabase.png")
    detection = Detection.objects.create(
        user=user,
        image=test_image,
        crop_type="Supabase Test",
        disease="Verified",
        confidence=99.9,
        recommendation="Connection is working perfectly!"
    )
    
    print(f"Record created in Django ORM with ID: {detection.id}")
    
    # 3. Verify via direct database query (to prove it went to Supabase)
    import psycopg2
    from dotenv import load_dotenv
    load_dotenv()
    
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    cur.execute("SELECT id, crop_type FROM detection_detection WHERE crop_type = 'Supabase Test' ORDER BY id DESC LIMIT 1;")
    row = cur.fetchone()
    
    if row and row[1] == 'Supabase Test':
        print(f"SUCCESS: Found record in Supabase (PostgreSQL) with ID: {row[0]}")
    else:
        print("FAILURE: Record not found in Supabase.")
        
    cur.close()
    conn.close()

if __name__ == "__main__":
    verify()
