from django.db import models

class CategoryGroup(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Category(models.Model):
    group = models.ForeignKey(
        CategoryGroup,
        related_name="categories",
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
