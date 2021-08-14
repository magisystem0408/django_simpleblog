"""
変数をビューからテンプレートに直接渡さなくても
テンプレート上で変数を使える仕組み
"""

from .models import Category



# 全てのカテゴリーデータを取得できるようになる
def common(request):
    category_data =Category.objects.all()
    context ={
        'category_data':category_data
    }
    return context