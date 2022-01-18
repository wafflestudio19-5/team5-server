from django.db.models import Avg, Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from lecture.models import Course, LectureEvaluation, Semester, TimeTable, Point, ExamInfo, ExamType
from lecture.serializers import CourseForEvalSerializer, EvalListSerializer, EvalCreateSerializer, \
    CourseSearchSerializer, MyCourseSerializer, ExamInfoCreateSerializer, ExamInfoListSerializer


class CourseInfoForEvalView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk=None):
        course = get_object_or_404(Course, pk=pk)
        if course.self_made:
            return Response('자신이 직접 추가한 강의에는 강의평가가 불가합니다.', status=status.HTTP_400_BAD_REQUEST)

        if not course.lecture_set.exists():
            course_sem = None
        else:
            course_sem = set()
            for obj in course.lecture_set.all():
                course_sem.add(obj.semester.name)
            course_sem = sorted(list(course_sem), reverse=True)

        serializer = CourseForEvalSerializer(course, context={'sem': course_sem})
        return Response(serializer.data, status=status.HTTP_200_OK)


class RecentEvalView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        evals = LectureEvaluation.objects.order_by('-created_at')
        serializer = EvalListSerializer(evals, many=True, context={'user': request.user})
        return Response(serializer.data, status.HTTP_200_OK)


class EvaluationView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk=None):
        course = get_object_or_404(Course, pk=pk)

        if course.self_made:
            return Response('자신이 직접 추가한 강의에는 강의평을 추가할 수 없습니다.', status=status.HTTP_400_BAD_REQUEST)
        if course.lectureevaluation_set.filter(writer=request.user).exists():
            return JsonResponse({
                'is_success': False     # "이미 강의평을 등록한 과목입니다.\n한 과목당 한 개의 강의평만 등록할 수 있습니다."
            })

        data = request.data.copy()
        sem = data.get('semester')  # string 값이 들어왔다 치면
        # semester validation은 따로
        course_sem = []
        for obj in course.lecture_set.all():
            course_sem.append(obj.semester.name)

        if sem is None:
            return Response('semester 값을 입력하세요.', status=status.HTTP_400_BAD_REQUEST)
        if sem not in course_sem:
            return Response('해당학기에 개설되지 않은 강의입니다. 학기 정보를 확인하세요.', status=status.HTTP_400_BAD_REQUEST)

        data['semester'] = Semester.objects.get(name=sem).id

        serializer = EvalCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['writer'] = request.user
        serializer.validated_data['course'] = course
        serializer.save()

        Point.objects.create(user=request.user, reason='강의평 작성', point=10)

        evals = LectureEvaluation.objects.filter(course=course).order_by('-created_at')
        return JsonResponse({
            'is_success': True,
            'evals': EvalListSerializer(evals, many=True, context={'user': request.user}).data,
        }, status=status.HTTP_201_CREATED)

    def get(self, request, pk=None):
        course = get_object_or_404(Course, pk=pk)
        if course.self_made:
            return Response('자신이 직접 추가한 강의에는 강의평이 존재하지 않습니다.', status=status.HTTP_400_BAD_REQUEST)

        evals = LectureEvaluation.objects.filter(course=course).order_by('-created_at')
        serializer = EvalListSerializer(evals, many=True, context={'user': request.user})
        return Response(serializer.data, status.HTTP_200_OK)


class MyCourseView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        # 강의평가 탭의 '내 강의평'에 뜨는 강의들이 언제 새학기 걸로 바뀌는지 모르겠어서
        # 9월~2월은 2학기의 기본시간표 리스트가 뜨고, 3월~8월은 1학기의 기본 시간표 리스트가 뜬다고 가정

        # semester 처리
        date = str(timezone.now())[:10].split('-')
        year = int(date[0])
        month = int(date[1])

        if month in range(3, 9):
            sem = str(year)+'년 1학기'
        elif month in range(1, 3):
            sem = str(year-1)+'년 2학기'
        else:
            sem = str(year)+'년 2학기'

        sem_id = Semester.objects.get(name=sem).id

        if TimeTable.objects.filter(user=request.user, is_default=True, semester=sem_id).exists():
            timetable = TimeTable.objects.get(user=request.user, is_default=True, semester=sem_id)
            my_course_ids = timetable.lecture.values_list('course')
            my_courses = Course.objects.filter(id__in=my_course_ids, self_made=False)
        else:
            my_courses = None

        point = Point.objects.filter(user=request.user).aggregate(Sum('point'))

        return JsonResponse({
            'point': point.get('point__sum'),
            'courses': MyCourseSerializer(my_courses, many=True, context={'user': request.user}).data
        }, status=status.HTTP_200_OK)


class EvalSummaryView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        if course.self_made:
            return Response('자신이 직접 추가한 강의에는 강의평이 존재하지 않습니다.', status=status.HTTP_400_BAD_REQUEST)
        evals = LectureEvaluation.objects.filter(course=course)

        if not evals.exists():
            return JsonResponse({
                'has_evals': False,
            }, status=status.HTTP_200_OK)

        avg_rating = round(evals.aggregate(Avg('rating')).get('rating__avg'), 2)
        # 아래 다섯개의 값은 most common 값을 들고오도록 함
        assignment = evals.values_list('assignment', flat=True).annotate(count=Count('assignment')).order_by("-count")[0]
        team = evals.values_list('team_project', flat=True).annotate(count=Count('team_project')).order_by("-count")[0]
        grade = evals.values_list('grade', flat=True).annotate(count=Count('grade')).order_by("-count")[0]
        attendance = evals.values_list('attendance', flat=True).annotate(count=Count('attendance')).order_by("-count")[0]
        exam_freq = evals.values_list('exam', flat=True).annotate(count=Count('exam')).order_by("-count")[0]

        # key에 해당하는 위의 값들을 value로 변환
        dict_AMOUNT_CHOICE = dict(LectureEvaluation.AMOUNT_CHOICES)
        assignment = dict_AMOUNT_CHOICE[assignment]
        team = dict_AMOUNT_CHOICE[team]
        grade = dict(LectureEvaluation.GRADE_CHOICES)[grade]
        attendance = dict(LectureEvaluation.ATTENDANCE_CHOICES)[attendance]
        exam_freq = dict(LectureEvaluation.EXAM_FREQUENCY_CHOICES)[exam_freq]

        return JsonResponse({
            'has_evals': True,
            'rating': avg_rating,
            'assignment': assignment,
            'team': team,
            'grade': grade,
            'attendance': attendance,
            'exam_freq': exam_freq,
        }, status=status.HTTP_200_OK)


class CourseSearchView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        data = request.data

        search = data.get('search')
        if search is None or len(search) == 1:
            return JsonResponse({
                'is_success': False,  # 검색어를 두 글자 이상 입력해주세요.
            })

        result = Course.objects.filter(self_made=False)
        result = result.filter(Q(title__icontains=search) | Q(instructor__icontains=search))
        if not result.exists():
            return Response(None, status.HTTP_200_OK)

        # 별점이 높은 순으로 정렬 --> 별점이 같다면 id가 빠른 순으로 정렬
        result = result.annotate(avg_rating=Avg('lectureevaluation__rating')).order_by("-avg_rating")
        serializer = CourseSearchSerializer(result, many=True)
        return Response(serializer.data, status.HTTP_200_OK)


class LikeEvaluationView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk, eval_pk):
        # course = get_object_or_404(Course, pk=pk) 아래 eval의 course가 이 course인지 확인할 순 있겠지만 하지 않는걸로,,
        eval = get_object_or_404(LectureEvaluation, pk=eval_pk)

        if request.user in eval.like_users.all():  # 이미 추천을 누른 사람이라면
            return JsonResponse({
                'is_success': False     # '이미 추천하였습니다.'를 담은 팝업창이 떠야함
            })
        else:
            eval.like_users.add(request.user)
            eval.num_of_likes += 1
            eval.save()
            return JsonResponse({
                'is_success': True,
                'value': eval.num_of_likes
            })

class ExamInfoView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk=None):
        course = get_object_or_404(Course, pk=pk)
        if course.self_made:
            return Response('자신이 직접 추가한 강의에는 시험 정보를 추가할 수 없습니다.', status=status.HTTP_400_BAD_REQUEST)

        # semester validation
        data = request.data.copy()
        sem = data.get('semester')  # string 값이 들어왔다 치면
        course_sem = []
        for obj in course.lecture_set.all():
            course_sem.append(obj.semester.name)

        if sem is None:
            return Response('semester 값을 입력하세요.', status=status.HTTP_400_BAD_REQUEST)
        if sem not in course_sem:
            return Response('해당학기에 개설되지 않은 강의입니다. 학기 정보를 확인하세요.', status=status.HTTP_400_BAD_REQUEST)

        data['semester'] = Semester.objects.get(name=sem).id

        serializer = ExamInfoCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        if course.examinfo_set.filter(writer=request.user, exam=data.get('exam')).exists():
            return JsonResponse({
                'is_success': False  # "이미 등록한 시험입니다. 한 시험에 한 번만 등록할 수 있습니다."
            })

        serializer.validated_data['writer'] = request.user
        serializer.validated_data['course'] = course
        types_input = None
        if 'types' in serializer.validated_data:
            types_input = serializer.validated_data.pop('types')
        exam_info = serializer.save()

        if not course.examinfo_set.exists():
            Point.objects.create(user=request.user, reason='시험 정보 공유', point=40)
        else:
            Point.objects.create(user=request.user, reason='시험 정보 공유', point=20)

        # type 추가
        if types_input:
            for type in types_input:
                input_type = ExamType.objects.get(type=type)
                exam_info.types.add(input_type)

        # readable_users에 글쓴이 추가
        exam_info.readable_users.add(request.user)

        exam_info = ExamInfo.objects.filter(course=course).order_by('-created_at')
        serializer = ExamInfoListSerializer(exam_info, many=True, context={'user': request.user})
        return JsonResponse({
            'is_success': True,
            'info': serializer.data
        }, status=status.HTTP_201_CREATED)

    def get(self, request, pk=None):
        course = get_object_or_404(Course, pk=pk)
        if course.self_made:
            return Response('자신이 직접 추가한 강의에는 시험 정보가 존재하지 않습니다.', status=status.HTTP_400_BAD_REQUEST)

        exam_info = ExamInfo.objects.filter(course=course).order_by('-created_at')
        serializer = ExamInfoListSerializer(exam_info, many=True, context={'user': request.user})
        return Response(serializer.data, status.HTTP_200_OK)


class LikeExamInfoView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk, exam_pk):
        # course = get_object_or_404(Course, pk=pk) 아래 examinfo의 course가 이 course인지 확인할 순 있겠지만 하지 않는걸로,,
        examinfo = get_object_or_404(ExamInfo, pk=exam_pk)

        if request.user not in examinfo.readable_users.all():
            return Response("readable user가 아니면 이 examinfo를 볼 수 없었을 텐데 어떻게 like를 누른거지", status=status.HTTP_400_BAD_REQUEST)

        if request.user in examinfo.like_users.all():  # 이미 추천을 누른 사람이라면
            return JsonResponse({
                'is_success': False    # '이미 추천하였습니다.'를 담은 팝업창이 떠야함
            })
        else:
            examinfo.like_users.add(request.user)
            examinfo.num_of_likes += 1
            examinfo.save()
            return JsonResponse({
                'is_success': True,
                'value': examinfo.num_of_likes
            })


# class UsePointView(APIView):
#     permission_classes = (permissions.IsAuthenticated,)
#
#     def post(self, request, pk=None):
#         course = get_object_or_404(Course, pk=pk)
#
#         nonreadable = ExamInfo.objects.filter(course=course).exclude(readable_users=request.user).order_by('-created_at')
#
#         if
#
#         Point.objects.create(user=request.user, reason='시험 정보 조회', point=-5)
#
#
# class MyPointView(APIView):
#     permission_classes = (permissions.IsAuthenticated,)
#
#     def get(self, request):