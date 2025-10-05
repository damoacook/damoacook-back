from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ExamBoardPagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        total = self.page.paginator.count
        per_page = self.page.paginator.per_page
        current = self.page.number
        start_no = total - (current - 1) * per_page

        numbered = []
        for i, item in enumerate(data):
            row = dict(item)  # OrderedDict → dict 복사
            row["no"] = max(start_no - i, 1) if total else 0
            numbered.append(row)

        return Response(
            {
                "total_count": total,
                "total_pages": self.page.paginator.num_pages,
                "current_page": current,
                "results": numbered,
            }
        )
