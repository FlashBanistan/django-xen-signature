from rest_framework import viewsets, views, status
from rest_framework.response import Response
from xen_signature.apps.pdf_to_image.models import Document
from xen_signature.apps.pdf_to_image.serializers import PdfToImageSerializer, DocumentSerializer


class DocumentToImageView(views.APIView):
    serializer_class = PdfToImageSerializer
    def post(self, request):
        serializer = PdfToImageSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            saved_data = serializer.save()
            # document = request.FILES['file']
            serialized_response = DocumentSerializer(context={'request': request}, instance=saved_data)
            return Response(status=status.HTTP_200_OK, data=serialized_response.data) 


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    queryset = Document.objects.all()