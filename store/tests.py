from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from store.models import Category, Product, Specification, ProductSpecification
from django.core.files.uploadedfile import SimpleUploadedFile

# Create your tests here.

class CategorySpecValueFilterTest(APITestCase):
    def setUp(self):
        # ساخت دسته‌بندی
        self.category = Category.objects.create(name="دسته تستی")
        # ساخت مشخصه
        self.spec = Specification.objects.create(name="RAM", data_type="int")
        self.spec.categories.add(self.category)
        # ساخت محصول و اتصال به دسته
        self.product = Product.objects.create(title="محصول تستی")
        self.product.categories.add(self.category)
        # ساخت مقدار مشخصه برای محصول
        self.ps = ProductSpecification.objects.create(product=self.product, specification=self.spec, int_value=8)

    def test_category_filter_by_spec_value(self):
        url = reverse('category-list') + f'?spec_value={self.spec.id}:{self.ps.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # باید دسته‌بندی ما در خروجی باشد
        ids = [item['id'] for item in response.data.get('results', [])]
        self.assertIn(self.category.id, ids)


class ProductImageS3Test(APITestCase):
    def test_product_image_upload_and_s3_url(self):
        # ساخت یک عکس تستی
        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        product = Product.objects.create(title="محصول با عکس", image=image)
        # بررسی اینکه url عکس به درستی به S3 اشاره می‌کند
        self.assertIsNotNone(product.image.url)
        self.assertTrue(product.image.url.startswith("https://s3.ir-thr-at1.arvanstorage.com/"))
        # همچنین می‌توان بررسی کرد که مسیر شامل نام باکت باشد
        from django.conf import settings
        self.assertIn(settings.ARVAN_BUCKET, product.image.url)
