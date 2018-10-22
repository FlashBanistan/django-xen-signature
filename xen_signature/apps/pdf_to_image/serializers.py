from io import BytesIO
from django.db import transaction
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import serializers
from wand.image import Image
from wand.color import Color
from PIL import Image as PI
from xen_signature.apps.pdf_to_image.models import DocumentImage, Document


VALID_EXTENSIONS = {'pdf', 'docx'}

class PdfToImageSerializer(serializers.Serializer):
    file = serializers.FileField()
    document_name = serializers.CharField(required=True)
    doc_ext = None

    def validate_file(self, document):
        # Determine valid document extension:
        doc_name = document.name
        doc_name_list = doc_name.split('.')
        self.doc_ext = doc_name_list[len(doc_name_list) - 1].lower()
        if self.doc_ext in VALID_EXTENSIONS:
            return document
        else:
            raise serializers.ValidationError('Not a valid extension.')
    
    @transaction.atomic
    def create(self, validated_data):
        # Create a document in which to store the images:
        document_name = validated_data.get('document_name')
        document = Document.objects.create(document_name=document_name)

        # Handle PDF:
        if self.doc_ext == 'pdf':
            pdf = validated_data.get('file')
            images_list = []
            image_pdf = Image(file=pdf, resolution=150)
            image_png = image_pdf.convert('png')
            for img in image_png.sequence:
                img_page = Image(image=img)
                # Remove transparency and replace with white background:
                img_page.background_color = Color('white')
                img_page.alpha_channel = 'remove'
                # Convert to blob and push to images list:
                images_list.append(img_page.make_blob('png'))
            # Save the images into a DocumentImage
            for page_no, img_data in enumerate(images_list):
                buffer = BytesIO()
                pi_image = PI.open(BytesIO(img_data))
                # Save pi_image into the buffer:
                pi_image.save(buffer, 'png')
                # Convert buffer into InMemoryFile:
                image_in_memory = InMemoryUploadedFile(buffer, None, 'test.png', 'image/png', buffer.getbuffer().nbytes, None)
                # Create the image and attach it to the document overlay:
                document_image = DocumentImage(document=document, page_no=page_no+1)
                document_image.image.save('test.png', image_in_memory)
                
        # Handle DOCX:        
        elif self.doc_ext == 'docx':
            pass

        return document


class DocumentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentImage
        fields = [
            'image',
            'image_height',
            'image_width',
            'page_no',
        ]
    

class DocumentSerializer(serializers.ModelSerializer):
    pages = DocumentImageSerializer(many=True, read_only=True)
    class Meta:
        model = Document
        fields = [
            'id',
            'document_name',
            'pages',
        ]
