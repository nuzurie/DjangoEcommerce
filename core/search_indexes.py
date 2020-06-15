# from haystack import indexes
# from core.models import Item
#
#
# class ItemIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.CharField(document=True, use_template=True)
#     item = indexes.CharField(model_attr='title')
#
#     def get_model(self):
#         return None
#
#     def index_queryset(self, using=None):
#         return self.get_model().objects.filter()
