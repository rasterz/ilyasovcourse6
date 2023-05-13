from rest_framework import serializers

from ads.models import Comment, Ad


# Сериалайзеры. Предлагаем Вам такую структуру, однако вы вправе использовать свою
class CommentSerializer(serializers.ModelSerializer):
    ad = serializers.SlugRelatedField(read_only=True, slug_field="title")
    author = serializers.SlugRelatedField(read_only=True, slug_field="first_name", )

    class Meta:
        model = Comment
        fields = ['id', 'ad', 'author', 'text', 'created_at', ]


class AdSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True, slug_field="first_name", )
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Ad
        fields = ["id", "author", "title", "price", "description", "image", "created_at", "comments", ]

    def get_comments(self, obj):
        return [CommentSerializer(com).data for com in obj.comments_by_ad.all()]


# ==== ПАМЯТКА === ЕЩЕ ОДИН ВАРИАНТ СИАРИАЛИЗАТОРА === ПАМЯТКА =============
# class CommentSerializer(serializers.ModelSerializer):
#     author_id = serializers.ReadOnlyField(source="author.id")
#     ad_id = serializers.ReadOnlyField(source="ad.id")
#     author_first_name = serializers.ReadOnlyField(source="author.first_name")
#     author_last_name = serializers.ReadOnlyField(source="author.last_name")
#     author_image = serializers.ImageField(source="author.image", read_only=True)
#
#     class Meta:
#         model = Comment
#         fields = ("pk", "text", "created_at", "author_id", "ad_id", "author_first_name",
#         "author_last_name", "author_image")
