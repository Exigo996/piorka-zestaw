from django.db import models
from django.forms import CheckboxSelectMultiple
from django.utils.text import slugify
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.models import Page, Orderable
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel


class ProductImage(Orderable):
    """Product image with ordering support"""
    product = ParentalKey('Product', on_delete=models.CASCADE, related_name='images')
    image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.CASCADE,
        related_name='+'
    )

    panels = [
        FieldPanel('image'),
    ]

    class Meta:
        verbose_name = "Zdjęcie produktu"
        verbose_name_plural = "Zdjęcia produktu"


class Product(ClusterableModel):
    # Choices for fields
    PRZEZNACZENIE_CHOICES = [
        ('kolczyki_para', 'Do ucha - kolczyki (para)'),
        ('kolczyki_asymetria', 'Do ucha - kolczyki (asymetria)'),
        ('kolczyki_single', 'Do ucha - kolczyki (single)'),
        ('kolczyki_komplet', 'Do ucha - kolczyki (komplet z wisiorkiem)'),
        ('zausznice', 'Zausznice'),
        ('na_szyje', 'Na szyję'),
        ('na_reke', 'Na rękę'),
        ('do_wlosow', 'Do włosów'),
        ('inne', 'Inne'),
    ]

    DLA_KOGO_CHOICES = [
        ('dla_niej', 'Dla niej'),
        ('dla_niego', 'Dla niego'),
        ('unisex', 'Unisex'),
    ]

    DLUGOSC_KATEGORIA_CHOICES = [
        ('krotkie', 'Krótkie'),
        ('srednie', 'Średnie'),
        ('dlugie', 'Długie'),
        ('bardzo_dlugie', 'Bardzo długie'),
    ]

    KOLOR_PIOR_CHOICES = [
        ('bezowy', 'Beżowy'),
        ('bialy', 'Biały'),
        ('brazowy', 'Brązowy'),
        ('czerwony', 'Czerwony'),
        ('czarny', 'Czarny'),
        ('granatowy', 'Granatowy'),
        ('niebieski', 'Niebieski'),
        ('rozowy', 'Różowy'),
        ('szary', 'Szary'),
        ('turkusowy', 'Turkusowy'),
        ('wzor', 'Wzór'),
        ('zolty', 'Żółty'),
        ('wielokolorowe', 'Wielokolorowe'),
    ]

    GATUNEK_PTAKOW_CHOICES = [
        ('bazant', 'Bażant'),
        ('emu', 'Emu'),
        ('gawron', 'Gawron'),
        ('indyk', 'Indyk'),
        ('kura_kogut', 'Kura lub kogut'),
        ('papuga', 'Papuga'),
        ('paw', 'Paw'),
        ('perlica', 'Perlica'),
        ('inny', 'Inny'),
    ]

    KOLOR_METALOWYCH_CHOICES = [
        ('zloty', 'Złoty'),
        ('srebrny', 'Srebrny'),
        ('mieszany', 'Mieszany'),
        ('inny', 'Inny'),
    ]

    RODZAJ_ZAPIECIA_CHOICES = [
        ('bigiel_otwarty', 'Bigiel otwarty'),
        ('bigiel_zamkniety', 'Bigiel zamknięty'),
        ('sztyft', 'Sztyft'),
        ('kolko', 'Kółko'),
        ('klips', 'Klips'),
        ('zausznik', 'Zausznik'),
        ('inny', 'Inny'),
        ('nie_dotyczy', 'Nie dotyczy'),
    ]

    # Basic fields
    name = models.CharField(max_length=255, verbose_name="Nazwa (ang.)")
    tytul = models.CharField(max_length=255, blank=True, verbose_name="Nazwa (pl.)")

    slug = models.SlugField(unique=True, blank=True, help_text="Automatycznie generowane z nazwy")
    
    description = models.TextField(blank=True, verbose_name="Opis (ang.)")
    opis = models.TextField(blank=True, verbose_name="Opis (pl.)")

    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cena podstawowa")
    cena = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Cena promocyjna")
    
    stripe_price_id = models.CharField(max_length=255, blank=True, help_text="Automatycznie generowane przez Stripe")
    stripe_product_id = models.CharField(max_length=255, blank=True, help_text="Automatycznie generowane przez Stripe")
    
    active = models.BooleanField(default=True, verbose_name="Czy dostepny w sklepie")

    featured = models.BooleanField(default=False, verbose_name="Wyróżnij na stronie głównej")

    # New fields
    nr_w_katalogu_zdjec = models.CharField(max_length=255, blank=True, verbose_name="Nr w katalogu zdjęć")
    przeznaczenie_ogolne = models.CharField(max_length=100, choices=PRZEZNACZENIE_CHOICES, blank=True, verbose_name="Przeznaczenie ogólne")
    dla_kogo = models.JSONField(default=list, blank=True, verbose_name="Dla kogo")
    dlugosc_kategoria = models.CharField(max_length=50, choices=DLUGOSC_KATEGORIA_CHOICES, blank=True, verbose_name="Długość kategoria")
    dlugosc_w_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Długość w cm")
    kolor_pior = models.JSONField(default=list, blank=True, verbose_name="Kolor piór w przewadze")
    gatunek_ptakow = models.JSONField(default=list, blank=True, verbose_name="Pióra zgubiły (gatunek)")
    kolor_elementow_metalowych = models.CharField(max_length=50, choices=KOLOR_METALOWYCH_CHOICES, blank=True, verbose_name="Kolor elementów metalowych")
    rodzaj_zapiecia = models.JSONField(default=list, blank=True, verbose_name="Rodzaj zapięcia")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        MultiFieldPanel([
            FieldPanel('slug'),
            FieldPanel('active'),
            FieldPanel('featured'),
        ], heading="Basic Info"),
        MultiFieldPanel([
            FieldPanel('tytul'),
            FieldPanel('name'),
            FieldPanel('nr_w_katalogu_zdjec'),
            FieldPanel('opis'),
            FieldPanel('description'),
        ], heading="Opisy"),
        MultiFieldPanel([
            FieldPanel('price'),
            FieldPanel('cena'),
        ], heading="Ceny"),
        InlinePanel('images', label="Zdjęcia", help_text="Pierwsze zdjęcie będzie wyświetlane jako główne w sklepie"),
        MultiFieldPanel([
            FieldPanel('przeznaczenie_ogolne'),
            FieldPanel('dla_kogo', widget=CheckboxSelectMultiple(choices=DLA_KOGO_CHOICES)),
        ], heading="Przeznaczenie"),
        MultiFieldPanel([
            FieldPanel('dlugosc_kategoria'),
            FieldPanel('dlugosc_w_cm'),
        ], heading="Wymiary"),
        MultiFieldPanel([
            FieldPanel('kolor_pior', widget=CheckboxSelectMultiple(choices=KOLOR_PIOR_CHOICES)),
            FieldPanel('gatunek_ptakow', widget=CheckboxSelectMultiple(choices=GATUNEK_PTAKOW_CHOICES)),
        ], heading="Pióra"),
        MultiFieldPanel([
            FieldPanel('kolor_elementow_metalowych'),
            FieldPanel('rodzaj_zapiecia', widget=CheckboxSelectMultiple(choices=RODZAJ_ZAPIECIA_CHOICES)),
        ], heading="Elementy metalowe i zapięcia"),
        MultiFieldPanel([
            FieldPanel('stripe_product_id'),
            FieldPanel('stripe_price_id'),
        ], heading="Stripe Integration"),
    ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def primary_image(self):
        """Returns the first image (main product image)"""
        first_image = self.images.first()
        return first_image.image if first_image else None

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

class HomePage(Page):
    pass
