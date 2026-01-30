from django import forms
from events.models import Category, Event, Participant

class StyleFormMixin:
    default_classes = "w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
    
    def apply_style_widgets(self):
        for field_name, field in self.fields.items():
            widget = field.widget
            
            if isinstance(widget, (forms.TextInput, forms.EmailInput, forms.URLInput)):
                widget.attrs['class'] = self.default_classes
                
            elif isinstance(widget, forms.Textarea):
                widget.attrs['class'] = self.default_classes
                widget.attrs['rows'] = 4
                
            elif isinstance(widget, forms.Select):
                widget.attrs['class'] = self.default_classes
                
            elif isinstance(widget, forms.DateInput):
                widget.attrs['class'] = self.default_classes
                widget.attrs['type'] = 'date'
                
            elif isinstance(widget, forms.TimeInput):
                widget.attrs['class'] = self.default_classes
                widget.attrs['type'] = 'time'
                
            elif isinstance(widget, forms.CheckboxSelectMultiple):
                widget.attrs['class'] = 'space-y-2'


class EventCategoryForm(StyleFormMixin, forms.Form):
   
    event_name = forms.CharField(
        max_length=250,
        label='Event Name',
        widget=forms.TextInput(attrs={'placeholder': 'Enter event name'})
    )
    event_description = forms.CharField(
        label='Event Description',
        widget=forms.Textarea(attrs={'placeholder': 'Enter event description', 'rows': 4})
    )
    event_date = forms.DateField(
        label='Event Date',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    event_time = forms.TimeField(
        label='Event Time',
        widget=forms.TimeInput(attrs={'type': 'time'})
    )
    event_location = forms.ChoiceField(
        label='Location',
        choices=Event.LOCATION_CHOICES
    )
    event_image = forms.CharField(
        max_length=250,
        required=False,
        label='Image Path (Optional)',
        widget=forms.TextInput(attrs={'placeholder': 'image/event1.jpg'})
    )
    
 
    use_existing_category = forms.BooleanField(
        required=False,
        initial=True,
        label='Use Existing Category',
        widget=forms.CheckboxInput(attrs={'class': 'mr-2'})
    )
    existing_category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label='Select Category',
        empty_label="-- Select Category --"
    )
    
    new_category_name = forms.CharField(
        max_length=250,
        required=False,
        label='New Category Name',
        widget=forms.TextInput(attrs={'placeholder': 'Enter new category name'})
    )
    new_category_description = forms.CharField(
        required=False,
        label='New Category Description',
        widget=forms.Textarea(attrs={'placeholder': 'Enter category description', 'rows': 2})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_style_widgets()
    
    def clean(self):
        cleaned_data = super().clean()
        use_existing = cleaned_data.get('use_existing_category')
        existing_cat = cleaned_data.get('existing_category')
        new_cat_name = cleaned_data.get('new_category_name')
        
        if use_existing and not existing_cat:
            raise forms.ValidationError("Please select an existing category.")
        
        if not use_existing and not new_cat_name:
            raise forms.ValidationError("Please provide a name for the new category.")
        
        return cleaned_data


class CategoryForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter category name'}),
            'description': forms.Textarea(attrs={'placeholder': 'Enter category description'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_style_widgets()


class EventForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Event
        fields = ['image', 'name', 'description', 'date', 'time', 'location', 'category']
        widgets = {
            'image': forms.TextInput(attrs={'placeholder': 'image/event1.jpg'}),
            'name': forms.TextInput(attrs={'placeholder': 'Enter event name'}),
            'description': forms.Textarea(attrs={'placeholder': 'Enter event description'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }
        labels = {
            'image': 'Image Path',
            'name': 'Event Name',
            'description': 'Description',
            'date': 'Event Date',
            'time': 'Event Time',
            'location': 'Location',
            'category': 'Category',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_style_widgets()
        self.fields['image'].required = False


class ParticipantForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['name', 'email'] 
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter your name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'your@email.com'}),
        }
        labels = {
            'name': 'Your Name',
            'email': 'Your Email',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_style_widgets()


class EventSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search events...',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'
        })
    )
    location = forms.ChoiceField(
        choices=[('', 'All Locations')] + Event.LOCATION_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'
        })
    )