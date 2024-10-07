# Prompt Vi:
```python
section_prompt = """Bạn đang hỗ trợ một bot được thiết kế để tự động ứng tuyển công việc trên AIHawk. Bot nhận được các câu hỏi khác nhau về đơn xin việc và cần xác định phần liên quan nhất của sơ yếu lý lịch để đưa ra câu trả lời chính xác.

        Đối với câu hỏi sau: '{question}', hãy xác định phần nào của sơ yếu lý lịch là liên quan nhất. 
        Trả lời chính xác một trong các lựa chọn sau:
        - Thông tin cá nhân
        - Tự nhận dạng
        - Ủy quyền pháp lý
        - Sở thích công việc
        - Chi tiết học vấn
        - Chi tiết kinh nghiệm
        - Dự án
        - Khả năng làm việc
        - Kỳ vọng lương
        - Chứng chỉ
        - Ngôn ngữ
        - Sở thích
        - Thư xin việc

        Dưới đây là hướng dẫn chi tiết để giúp bạn chọn đúng phần:

        1. **Thông tin cá nhân**:
        - **Mục đích**: Chứa thông tin liên hệ cơ bản và hồ sơ trực tuyến của bạn.
        - **Sử dụng khi**: Câu hỏi liên quan đến cách liên hệ với bạn hoặc yêu cầu liên kết đến sự hiện diện chuyên nghiệp trực tuyến của bạn.
        - **Ví dụ**: Địa chỉ email, số điện thoại, hồ sơ AIHawk, kho lưu trữ GitHub, trang web cá nhân.

        2. **Tự nhận dạng**:
        - **Mục đích**: Bao gồm các định danh cá nhân và thông tin nhân khẩu học.
        - **Sử dụng khi**: Câu hỏi liên quan đến giới tính, đại từ nhân xưng, tình trạng cựu chiến binh, tình trạng khuyết tật hoặc dân tộc của bạn.
        - **Ví dụ**: Giới tính, đại từ nhân xưng, tình trạng cựu chiến binh, tình trạng khuyết tật, dân tộc.

        3. **Ủy quyền pháp lý**:
        - **Mục đích**: Chi tiết về tình trạng ủy quyền làm việc và yêu cầu visa của bạn.
        - **Sử dụng khi**: Câu hỏi liên quan đến khả năng làm việc của bạn ở các quốc gia cụ thể hoặc nếu bạn cần tài trợ hoặc visa.
        - **Ví dụ**: Ủy quyền làm việc tại EU và Hoa Kỳ, yêu cầu visa, được phép làm việc hợp pháp.

        4. **Sở thích công việc**:
        - **Mục đích**: Chỉ rõ sở thích của bạn về điều kiện làm việc và vai trò công việc.
        - **Sử dụng khi**: Câu hỏi liên quan đến sở thích của bạn về làm việc từ xa, làm việc trực tiếp, di chuyển và sẵn sàng tham gia đánh giá hoặc kiểm tra lý lịch.
        - **Ví dụ**: Làm việc từ xa, làm việc trực tiếp, sẵn sàng di chuyển, sẵn sàng hoàn thành các đánh giá.

        5. **Chi tiết học vấn**:
        - **Mục đích**: Chứa thông tin về trình độ học vấn của bạn.
        - **Sử dụng khi**: Câu hỏi liên quan đến bằng cấp, trường đại học đã học, điểm trung bình và các khóa học liên quan.
        - **Ví dụ**: Bằng cấp, trường đại học, điểm trung bình, lĩnh vực học tập, kỳ thi.

        6. **Chi tiết kinh nghiệm**:
        - **Mục đích**: Chi tiết về lịch sử làm việc chuyên nghiệp và trách nhiệm chính của bạn.
        - **Sử dụng khi**: Câu hỏi liên quan đến vai trò công việc, trách nhiệm và thành tích của bạn trong các vị trí trước đây.
        - **Ví dụ**: Vị trí công việc, tên công ty, trách nhiệm chính, kỹ năng đã đạt được.

        7. **Dự án**:
        - **Mục đích**: Nêu bật các dự án cụ thể mà bạn đã làm việc.
        - **Sử dụng khi**: Câu hỏi liên quan đến các dự án cụ thể, mô tả về chúng hoặc liên kết đến kho lưu trữ dự án.
        - **Ví dụ**: Tên dự án, mô tả, liên kết đến kho lưu trữ dự án.

        8. **Khả năng làm việc**:
        - **Mục đích**: Cung cấp thông tin về khả năng làm việc của bạn cho các vai trò mới.
        - **Sử dụng khi**: Câu hỏi liên quan đến việc bạn có thể bắt đầu công việc mới sớm như thế nào hoặc thời gian thông báo của bạn.
        - **Ví dụ**: Thời gian thông báo, khả năng bắt đầu.

        9. **Kỳ vọng lương**:
        - **Mục đích**: Bao gồm phạm vi lương mong đợi của bạn.
        - **Sử dụng khi**: Câu hỏi liên quan đến kỳ vọng lương hoặc yêu cầu về thù lao của bạn.
        - **Ví dụ**: Phạm vi lương mong muốn.

        10. **Chứng chỉ**:
            - **Mục đích**: Liệt kê các chứng chỉ hoặc giấy phép chuyên môn của bạn.
            - **Sử dụng khi**: Câu hỏi liên quan đến chứng chỉ hoặc trình độ của bạn từ các tổ chức được công nhận.
            - **Ví dụ**: Tên chứng chỉ, cơ quan cấp, ngày có hiệu lực.

        11. **Ngôn ngữ**:
            - **Mục đích**: Mô tả các ngôn ngữ bạn có thể nói và trình độ thành thạo của bạn.
            - **Sử dụng khi**: Câu hỏi liên quan đến kỹ năng ngôn ngữ của bạn hoặc trình độ thành thạo các ngôn ngữ cụ thể.
            - **Ví dụ**: Ngôn ngữ nói được, mức độ thành thạo.

        12. **Sở thích**:
            - **Mục đích**: Chi tiết về sở thích cá nhân hoặc chuyên môn của bạn.
            - **Sử dụng khi**: Câu hỏi liên quan đến sở thích, mối quan tâm hoặc hoạt động ngoài công việc của bạn.
            - **Ví dụ**: Sở thích cá nhân, mối quan tâm chuyên môn.

        13. **Thư xin việc**:
            - **Mục đích**: Chứa thư xin việc hoặc tuyên bố cá nhân của bạn.
            - **Sử dụng khi**: Câu hỏi liên quan đến thư xin việc của bạn hoặc nội dung viết cụ thể dành cho đơn xin việc.
            - **Ví dụ**: Nội dung thư xin việc, tuyên bố cá nhân.

        Chỉ cung cấp chính xác tên của phần từ danh sách trên mà không có thêm bất kỳ văn bản nào khác.
        """
```