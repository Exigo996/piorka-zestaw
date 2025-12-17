from django.db import models
from django.core.exceptions import ValidationError
from django import forms
from django.utils.text import slugify
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.models import Page, Orderable
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel


class ProductAdminForm(forms.ModelForm):
    """Custom form for Product admin with proper multiselect handling"""

    dla_kogo = forms.MultipleChoiceField(
        choices=[],  # Will be set in __init__
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Dla kogo"
    )

    kolor_pior = forms.MultipleChoiceField(
        choices=[],
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Kolor piór w przewadze"
    )

    gatunek_ptakow = forms.MultipleChoiceField(
        choices=[],
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Pióra zgubiły (gatunek)"
    )

    rodzaj_zapiecia = forms.MultipleChoiceField(
        choices=[],
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Rodzaj zapięcia"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set choices from model
        self.fields['dla_kogo'].choices = Product.DLA_KOGO_CHOICES
        self.fields['kolor_pior'].choices = Product.KOLOR_PIOR_CHOICES
        self.fields['gatunek_ptakow'].choices = Product.GATUNEK_PTAKOW_CHOICES
        self.fields['rodzaj_zapiecia'].choices = Product.RODZAJ_ZAPIECIA_CHOICES

        # Set initial values from instance
        if self.instance and self.instance.pk:
            if self.instance.dla_kogo:
                self.fields['dla_kogo'].initial = self.instance.dla_kogo
            if self.instance.kolor_pior:
                self.fields['kolor_pior'].initial = self.instance.kolor_pior
            if self.instance.gatunek_ptakow:
                self.fields['gatunek_ptakow'].initial = self.instance.gatunek_ptakow
            if self.instance.rodzaj_zapiecia:
                self.fields['rodzaj_zapiecia'].initial = self.instance.rodzaj_zapiecia


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
    nr_w_katalogu_zdjec = models.CharField(max_length=255, blank=True, default='', verbose_name="Nr w katalogu zdjęć")
    przeznaczenie_ogolne = models.CharField(max_length=255, choices=PRZEZNACZENIE_CHOICES, blank=True, default='', verbose_name="Przeznaczenie ogólne")
    dla_kogo = models.JSONField(default=list, blank=True, null=False, verbose_name="Dla kogo")
    dlugosc_kategoria = models.CharField(max_length=255, choices=DLUGOSC_KATEGORIA_CHOICES, blank=True, default='', verbose_name="Długość kategoria")
    dlugosc_w_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Długość w cm")
    kolor_pior = models.JSONField(default=list, blank=True, null=False, verbose_name="Kolor piór w przewadze")
    gatunek_ptakow = models.JSONField(default=list, blank=True, null=False, verbose_name="Pióra zgubiły (gatunek)")
    kolor_elementow_metalowych = models.CharField(max_length=255, choices=KOLOR_METALOWYCH_CHOICES, blank=True, default='', verbose_name="Kolor elementów metalowych")
    rodzaj_zapiecia = models.JSONField(default=list, blank=True, null=False, verbose_name="Rodzaj zapięcia")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    base_form_class = ProductAdminForm

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
            FieldPanel('dla_kogo'),
        ], heading="Przeznaczenie"),
        MultiFieldPanel([
            FieldPanel('dlugosc_kategoria'),
            FieldPanel('dlugosc_w_cm'),
        ], heading="Wymiary"),
        MultiFieldPanel([
            FieldPanel('kolor_pior'),
            FieldPanel('gatunek_ptakow'),
        ], heading="Pióra"),
        MultiFieldPanel([
            FieldPanel('kolor_elementow_metalowych'),
            FieldPanel('rodzaj_zapiecia'),
        ], heading="Elementy metalowe i zapięcia"),
        MultiFieldPanel([
            FieldPanel('stripe_product_id'),
            FieldPanel('stripe_price_id'),
        ], heading="Stripe Integration"),
    ]

    def clean(self):
        """Validate model fields before saving"""
        errors = {}

        # Validate required fields
        if not self.name or not self.name.strip():
            errors['name'] = 'Nazwa (ang.) jest wymagana'

        if not self.price or self.price <= 0:
            errors['price'] = 'Cena podstawowa musi być większa niż 0'

        # Validate JSONField fields are lists
        if self.dla_kogo is not None and not isinstance(self.dla_kogo, list):
            errors['dla_kogo'] = 'Nieprawidłowy format danych'

        if self.kolor_pior is not None and not isinstance(self.kolor_pior, list):
            errors['kolor_pior'] = 'Nieprawidłowy format danych'

        if self.gatunek_ptakow is not None and not isinstance(self.gatunek_ptakow, list):
            errors['gatunek_ptakow'] = 'Nieprawidłowy format danych'

        if self.rodzaj_zapiecia is not None and not isinstance(self.rodzaj_zapiecia, list):
            errors['rodzaj_zapiecia'] = 'Nieprawidłowy format danych'

        # Validate choice fields have valid values
        if self.przeznaczenie_ogolne and self.przeznaczenie_ogolne not in dict(self.PRZEZNACZENIE_CHOICES):
            errors['przeznaczenie_ogolne'] = 'Nieprawidłowa wartość'

        if self.dlugosc_kategoria and self.dlugosc_kategoria not in dict(self.DLUGOSC_KATEGORIA_CHOICES):
            errors['dlugosc_kategoria'] = 'Nieprawidłowa wartość'

        if self.kolor_elementow_metalowych and self.kolor_elementow_metalowych not in dict(self.KOLOR_METALOWYCH_CHOICES):
            errors['kolor_elementow_metalowych'] = 'Nieprawidłowa wartość'

        # Validate multiselect choices
        for choice in self.dla_kogo or []:
            if choice not in dict(self.DLA_KOGO_CHOICES):
                errors['dla_kogo'] = f'Nieprawidłowa wartość: {choice}'
                break

        for choice in self.kolor_pior or []:
            if choice not in dict(self.KOLOR_PIOR_CHOICES):
                errors['kolor_pior'] = f'Nieprawidłowa wartość: {choice}'
                break

        for choice in self.gatunek_ptakow or []:
            if choice not in dict(self.GATUNEK_PTAKOW_CHOICES):
                errors['gatunek_ptakow'] = f'Nieprawidłowa wartość: {choice}'
                break

        for choice in self.rodzaj_zapiecia or []:
            if choice not in dict(self.RODZAJ_ZAPIECIA_CHOICES):
                errors['rodzaj_zapiecia'] = f'Nieprawidłowa wartość: {choice}'
                break

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Auto-generate slug from name
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # Ensure JSONField fields are never NULL, always use empty list
        if self.dla_kogo is None:
            self.dla_kogo = []
        if self.kolor_pior is None:
            self.kolor_pior = []
        if self.gatunek_ptakow is None:
            self.gatunek_ptakow = []
        if self.rodzaj_zapiecia is None:
            self.rodzaj_zapiecia = []

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
