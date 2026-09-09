# apps/accounts/forms.py - COMPLETE CORRECTED FILE

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from PIL import Image
from django.core.exceptions import ValidationError
from django.core.serializers import python
from apps.core.models import Subject, Chapter, Topic, Question, QuestionDifficulty
import hashlib
import json

User = get_user_model()


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "email",
            "full_name",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["email"].widget.attrs.update({
            "class": "form-control",
            "autocomplete": "email",
        })

        self.fields["full_name"].widget.attrs.update({
            "class": "form-control",
            "autocomplete": "name",
        })

        self.fields["password1"].widget.attrs.update({
            "class": "form-control",
            "autocomplete": "new-password",
        })

        self.fields["password2"].widget.attrs.update({
            "class": "form-control",
            "autocomplete": "new-password",
        })

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "An account with this email address already exists."
            )

        return email


class LoginForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "autocomplete": "email",
            }
        ),
    )

    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "autocomplete": "current-password",
            }
        ),
    )


# apps/accounts/forms.py - Update ProfileForm

class ProfileForm(forms.Form):
    full_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "name",
            },
        ),
    )

    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "tel",
            },
        ),
    )

    profile_picture = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control",
                "accept": "image/jpeg,image/png",
            },
        ),
    )

    def __init__(self, *args, user=None, profile=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = user
        self.profile = profile

        if user is not None:
            self.fields["full_name"].initial = user.full_name

        if profile is not None:
            self.fields["phone_number"].initial = profile.phone_number

    def clean_full_name(self):
        full_name = self.cleaned_data["full_name"].strip()

        if not full_name:
            raise forms.ValidationError(
                "Full name is required."
            )

        return full_name

    def clean_phone_number(self):
        return self.cleaned_data["phone_number"].strip()

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get("profile_picture")

        if not profile_picture:
            return profile_picture

        max_size = 5 * 1024 * 1024

        if profile_picture.size > max_size:
            raise forms.ValidationError(
                "Profile picture must be 5 MB or smaller."
            )

        try:
            from PIL import Image
            image = Image.open(profile_picture)
            image.verify()

            profile_picture.seek(0)

            image = Image.open(profile_picture)
            image_format = image.format

            if image_format not in ("JPEG", "PNG"):
                raise forms.ValidationError(
                    "Profile picture must be a JPEG or PNG image."
                )

            profile_picture.seek(0)

        except forms.ValidationError:
            raise

        except Exception:
            raise forms.ValidationError(
                "Please upload a valid image file."
            )

        return profile_picture


class QuestionForm(forms.ModelForm):
    """
    Admin form for manually creating/editing questions.

    Form structure matches the JSON question format:

    {
        "subject": "...",
        "chapter": "...",
        "topic": "...",
        "question": "...",
        "option_a": "...",
        "option_b": "...",
        "option_c": "...",
        "option_d": "...",
        "correct_answer": "A",
        "explanation": "...",
        "difficulty": "Easy",
        "source": "...",
        "year_tag": ""
    }
    """

    # ---------------------------------------------------------
    # TAXONOMY
    # ---------------------------------------------------------

    subject = forms.ModelChoiceField(
        queryset=Subject.objects.filter(is_active=True),
        required=True,
        empty_label="Select Subject",
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "id": "id_subject",
            }
        ),
    )

    chapter = forms.ModelChoiceField(
        queryset=Chapter.objects.none(),
        required=True,
        empty_label="Select Chapter",
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "id": "id_chapter",
            }
        ),
    )

    topic = forms.ModelChoiceField(
        queryset=Topic.objects.none(),
        required=True,
        empty_label="Select Topic",
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "id": "id_topic",
            }
        ),
    )

    # ---------------------------------------------------------
    # ANSWER
    # ---------------------------------------------------------

    correct_answer = forms.ChoiceField(
        choices=[
            ("A", "Option A"),
            ("B", "Option B"),
            ("C", "Option C"),
            ("D", "Option D"),
        ],
        required=True,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    # ---------------------------------------------------------
    # DIFFICULTY
    # ---------------------------------------------------------

    difficulty = forms.ChoiceField(
        choices=QuestionDifficulty.choices,
        required=True,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    # ---------------------------------------------------------
    # MODEL FIELDS
    # ---------------------------------------------------------

    class Meta:
        model = Question

        fields = [
            "question",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "correct_answer",
            "explanation",
            "difficulty",
            "source",
            "year_tag",
            "is_active",
        ]

        widgets = {
            "question": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": (
                        "Which organelle is known as "
                        "the powerhouse of the cell?"
                    ),
                }
            ),

            "option_a": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Mitochondria",
                }
            ),

            "option_b": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ribosome",
                }
            ),

            "option_c": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nucleus",
                }
            ),

            "option_d": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Golgi apparatus",
                }
            ),

            "explanation": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Mitochondria produce ATP.",
                }
            ),

            "source": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "NCERT",
                }
            ),

            "year_tag": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 2024, NEET 2023",
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

        labels = {
            "question": "Question",
            "option_a": "Option A",
            "option_b": "Option B",
            "option_c": "Option C",
            "option_d": "Option D",
            "correct_answer": "Correct Answer",
            "explanation": "Explanation",
            "difficulty": "Difficulty",
            "source": "Source",
            "year_tag": "Year Tag",
            "is_active": "Active",
        }

        help_texts = {
            "source": "Example: NCERT, NEET, Previous Year Question",
            "year_tag": "Optional. Example: 2024 or NEET 2023",
        }

    # ---------------------------------------------------------
    # INITIALIZATION
    # ---------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Editing an existing question
        if self.instance.pk and self.instance.topic:
            topic = self.instance.topic
            chapter = topic.chapter
            subject = chapter.subject

            self.fields["subject"].initial = subject

            self.fields["chapter"].queryset = Chapter.objects.filter(
                subject=subject,
                is_active=True,
            )

            self.fields["chapter"].initial = chapter

            self.fields["topic"].queryset = Topic.objects.filter(
                chapter=chapter,
                is_active=True,
            )

            self.fields["topic"].initial = topic

        # Creating/editing after validation failure
        if self.data.get("subject"):
            try:
                subject_id = int(self.data.get("subject"))

                self.fields["chapter"].queryset = Chapter.objects.filter(
                    subject_id=subject_id,
                    is_active=True,
                )
            except (ValueError, TypeError):
                pass

        elif self.fields["subject"].initial:
            self.fields["chapter"].queryset = Chapter.objects.filter(
                subject=self.fields["subject"].initial,
                is_active=True,
            )

        if self.data.get("chapter"):
            try:
                chapter_id = int(self.data.get("chapter"))

                self.fields["topic"].queryset = Topic.objects.filter(
                    chapter_id=chapter_id,
                    is_active=True,
                )
            except (ValueError, TypeError):
                pass

        elif self.fields["chapter"].initial:
            self.fields["topic"].queryset = Topic.objects.filter(
                chapter=self.fields["chapter"].initial,
                is_active=True,
            )

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------

    def clean(self):
        cleaned_data = super().clean()

        subject = cleaned_data.get("subject")
        chapter = cleaned_data.get("chapter")
        topic = cleaned_data.get("topic")

        option_a = cleaned_data.get("option_a")
        option_b = cleaned_data.get("option_b")
        option_c = cleaned_data.get("option_c")
        option_d = cleaned_data.get("option_d")

        correct_answer = cleaned_data.get("correct_answer")

        # ---------------------------------------------
        # Required taxonomy
        # ---------------------------------------------

        if not subject:
            raise ValidationError(
                "Please select a subject."
            )

        if not chapter:
            raise ValidationError(
                "Please select a chapter."
            )

        if not topic:
            raise ValidationError(
                "Please select a topic."
            )

        # ---------------------------------------------
        # Hierarchy validation
        # ---------------------------------------------

        if chapter and subject:
            if chapter.subject_id != subject.id:
                raise ValidationError(
                    "Selected chapter does not belong "
                    "to the selected subject."
                )

        if topic and chapter:
            if topic.chapter_id != chapter.id:
                raise ValidationError(
                    "Selected topic does not belong "
                    "to the selected chapter."
                )

        # ---------------------------------------------
        # Options
        # ---------------------------------------------

        if not option_a:
            raise ValidationError("Option A cannot be empty.")

        if not option_b:
            raise ValidationError("Option B cannot be empty.")

        if not option_c:
            raise ValidationError("Option C cannot be empty.")

        if not option_d:
            raise ValidationError("Option D cannot be empty.")

        # ---------------------------------------------
        # Correct answer
        # ---------------------------------------------

        option_map = {
            "A": option_a,
            "B": option_b,
            "C": option_c,
            "D": option_d,
        }

        if correct_answer not in option_map:
            raise ValidationError(
                "Correct answer must be A, B, C, or D."
            )

        if not option_map[correct_answer]:
            raise ValidationError(
                f"Option {correct_answer} is empty "
                "but marked as correct."
            )

        return cleaned_data

    # ---------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------

    def save(self, commit=True):
        question = super().save(commit=False)

        # Question.topic is the actual FK stored in the DB.
        question.topic = self.cleaned_data["topic"]

        # Generate fingerprint from current question content.
        question.question_fingerprint = self._generate_fingerprint()

        if commit:
            question.save()

        return question

    # ---------------------------------------------------------
    # FINGERPRINT
    # ---------------------------------------------------------

    def _generate_fingerprint(self):
        """
        Generate SHA-256 fingerprint used for duplicate detection.
        """

        data = {
            "question": self.cleaned_data.get("question", "").strip(),
            "options": [
                self.cleaned_data.get("option_a", "").strip(),
                self.cleaned_data.get("option_b", "").strip(),
                self.cleaned_data.get("option_c", "").strip(),
                self.cleaned_data.get("option_d", "").strip(),
            ],
            "correct_answer": self.cleaned_data.get(
                "correct_answer",
                "",
            ),
        }

        text = json.dumps(
            data,
            sort_keys=True,
        )

        return hashlib.sha256(
            text.encode("utf-8")
        ).hexdigest()


# ================================================================
# NEW FORMS FOR IMPORT AND FILTERING
# ================================================================

class QuestionImportForm(forms.Form):
    """Form for importing questions from JSON or CSV"""
    
    IMPORT_TYPE_CHOICES = [
        ('json', 'JSON File'),
        ('csv', 'CSV File'),
    ]
    
    import_type = forms.ChoiceField(
        choices=IMPORT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.json,.csv'
        })
    )
    
    create_missing = forms.BooleanField(
        required=False,
        initial=True,
        help_text="Automatically create subjects, chapters, and topics if they don't exist.",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    skip_duplicates = forms.BooleanField(
        required=False,
        initial=True,
        help_text="Skip questions that already exist in the database.",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file:
            raise ValidationError("Please select a file.")
        
        # Check file extension
        import_type = self.cleaned_data.get('import_type')
        ext = file.name.split('.')[-1].lower()
        
        if import_type == 'json' and ext != 'json':
            raise ValidationError("Please upload a JSON file.")
        if import_type == 'csv' and ext != 'csv':
            raise ValidationError("Please upload a CSV file.")
        
        return file


class QuestionFilterForm(forms.Form):
    """Form for filtering questions in the list view"""
    
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.filter(is_active=True),
        required=False,
        empty_label="All Subjects",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    chapter = forms.ModelChoiceField(
        queryset=Chapter.objects.none(),
        required=False,
        empty_label="All Chapters",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    topic = forms.ModelChoiceField(
        queryset=Topic.objects.none(),
        required=False,
        empty_label="All Topics",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    difficulty = forms.ChoiceField(
        choices=[('', 'All Difficulties')] + list(QuestionDifficulty.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search questions...'
        })
    )
    
    is_active = forms.ChoiceField(
        choices=[
            ('', 'All'),
            ('true', 'Active Only'),
            ('false', 'Inactive Only'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Dynamic chapter/topic filtering
        if 'subject' in self.data:
            try:
                subject_id = int(self.data.get('subject'))
                self.fields['chapter'].queryset = Chapter.objects.filter(
                    subject_id=subject_id, is_active=True
                )
            except (ValueError, TypeError):
                pass
        
        if 'chapter' in self.data:
            try:
                chapter_id = int(self.data.get('chapter'))
                self.fields['topic'].queryset = Topic.objects.filter(
                    chapter_id=chapter_id, is_active=True
                )
            except (ValueError, TypeError):
                pass