from django.shortcuts import render
from .models import Clazz # <-- Import model Clazz
from django.shortcuts import render, get_object_or_404

# Create your views here.
def home(request):
    """
    This view renders the home page.
    """
    # Lấy 3 lớp học đầu tiên, sắp xếp theo ID giảm dần
    featured_classes = Clazz.objects.all().order_by('-class_id')[:3]
    
    context = {
        'classes': featured_classes
    }
    return render(request, 'core/home.html', context)

def class_list(request):
    """
    This view fetches and displays all available classes.
    """
    all_classes = Clazz.objects.all().order_by('class_name') # Lấy tất cả lớp học
    
    context = {
        'classes': all_classes
    }
    return render(request, 'core/class_list.html', context)

def class_detail(request, pk):
    """
    Hiển thị thông tin chi tiết của một lớp học duy nhất.
    """
    # Lấy đối tượng Clazz có pk tương ứng, hoặc trả về lỗi 404 nếu không tìm thấy.
    clazz = get_object_or_404(Clazz, pk=pk)
    
    context = {
        'clazz': clazz,
        # Bạn có thể truyền thêm dữ liệu liên quan ở đây, ví dụ danh sách học viên
        'enrollments': clazz.enrollments.all()
    }
    return render(request, 'core/class_detail.html', context)