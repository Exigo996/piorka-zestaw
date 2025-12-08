from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.models import Page

class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_price_id = models.CharField(max_length=255, blank=True, help_text="Stripe Price ID for checkout")
    stripe_product_id = models.CharField(max_length=255, blank=True, help_text="Stripe Product ID")
    active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False, verbose_name="Wyróżnij na stronie głównej")
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('slug'),
            FieldPanel('active'),
            FieldPanel('featured'),
        ], heading="Basic Info"),
        FieldPanel('description'),
        FieldPanel('price'),
        FieldPanel('image'),
        MultiFieldPanel([
            FieldPanel('stripe_product_id'),
            FieldPanel('stripe_price_id'),
        ], heading="Stripe Integration"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

class HomePage(Page):
    pass
