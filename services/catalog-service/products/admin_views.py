from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from craft_common.auth.permissions import HasRole
from products.models import Product

class AdminProductsView(APIView):
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def get(self, request):
        products = Product.objects.all()[:100]
        data = [{
            'id': str(p.id),
            'ProductName': p.ProductName,
            'category': getattr(p.Category, 'Title', '') if getattr(p, 'Category', None) else '',
            'UnitPrice': float(p.UnitPrice) if getattr(p, 'UnitPrice', None) else 0,
            'Stock': p.Stock if hasattr(p, 'Stock') else 0,
            'supplier_name': p.supplier_name if hasattr(p, 'supplier_name') else '',
            'Rating': float(p.Rating) if hasattr(p, 'Rating') and p.Rating else 0.0,
            'DiscountPercentage': float(p.DiscountPercentage) if hasattr(p, 'DiscountPercentage') and p.DiscountPercentage else 0.0,
            'OutOfStock': p.OutOfStock if hasattr(p, 'OutOfStock') else False,
            'images': [{'image': img.image.url} for img in p.images.all()] if hasattr(p, 'images') else [],
            'status': 'active' if getattr(p, 'is_active', True) else 'inactive'
        } for p in products]
        return Response(data)

class AdminProductModerationView(APIView):
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def get(self, request):
        products = Product.objects.filter(publish_status=Product.PublishStatus.PENDING)
        data = [{
            'id': p.id,
            'ProductName': p.ProductName,
            'Supplier': p.supplier_name or f"Supplier {p.supplier_id}",
            'UnitPrice': float(p.UnitPrice) if p.UnitPrice else 0.0,
            'Publish_Date': p.Publish_Date.isoformat() if p.Publish_Date else None
        } for p in products]
        return Response(data)

class AdminProductModerationActionView(APIView):
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def post(self, request, pk):
        try:
            p = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)
        
        action = request.data.get("action")
        if action == "approve":
            p.publish_status = Product.PublishStatus.APPROVED
        elif action == "reject":
            p.publish_status = Product.PublishStatus.REJECTED
        else:
            return Response({"detail": "Invalid action"}, status=400)
            
        p.save(update_fields=['publish_status'])
        return Response({"status": "success", "new_status": p.publish_status})
