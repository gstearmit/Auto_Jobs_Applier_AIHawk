# Mẫu thông tin cá nhân
personal_information_template = """
Trả lời câu hỏi sau dựa trên thông tin cá nhân được cung cấp.

## Quy tắc
- Trả lời câu hỏi trực tiếp.

## Ví dụ
Sơ yếu lý lịch của tôi: John Doe, sinh ngày 01/01/1990, sống tại Milan, Ý.
Câu hỏi: Thành phố của bạn là gì?
 Milan

Thông tin cá nhân: {resume_section}
Câu hỏi: {question}
"""

# Mẫu tự nhận dạng
self_identification_template = """
Trả lời câu hỏi sau dựa trên chi tiết tự nhận dạng được cung cấp.

## Quy tắc
- Trả lời câu hỏi trực tiếp.

## Ví dụ
Sơ yếu lý lịch của tôi: Nam, sử dụng đại từ anh ấy/của anh ấy, không phải cựu chiến binh, không có khuyết tật.
Câu hỏi: Giới tính của bạn là gì?
Nam

Tự nhận dạng: {resume_section}
Câu hỏi: {question}
"""

# Mẫu ủy quyền pháp lý
legal_authorization_template = """
Trả lời câu hỏi sau dựa trên chi tiết ủy quyền pháp lý được cung cấp.

## Quy tắc
- Trả lời câu hỏi trực tiếp.

## Ví dụ
Sơ yếu lý lịch của tôi: Được phép làm việc tại EU, không cần visa Mỹ.
Câu hỏi: Bạn có được phép làm việc hợp pháp tại EU không?
Có

Ủy quyền pháp lý: {resume_section}
Câu hỏi: {question}
"""

# Mẫu sở thích làm việc
work_preferences_template = """
Trả lời câu hỏi sau dựa trên sở thích làm việc được cung cấp.

## Quy tắc
- Trả lời câu hỏi trực tiếp.

## Ví dụ
Sơ yếu lý lịch của tôi: Sẵn sàng làm việc từ xa, sẵn sàng di chuyển.
Câu hỏi: Bạn có sẵn sàng làm việc từ xa không?
Có

Sở thích làm việc: {resume_section}
Câu hỏi: {question}
"""

# Mẫu chi tiết giáo dục
education_details_template = """
Trả lời câu hỏi sau dựa trên chi tiết giáo dục được cung cấp.

## Quy tắc
- Trả lời câu hỏi trực tiếp.
- Nếu có vẻ như bạn có kinh nghiệm, ngay cả khi không được định nghĩa rõ ràng, hãy trả lời như thể bạn có kinh nghiệm.
- Nếu không chắc chắn, hãy trả lời "Tôi không có kinh nghiệm về điều đó, nhưng tôi học nhanh" hoặc "Chưa, nhưng sẵn sàng học hỏi."
- Giữ câu trả lời dưới 140 ký tự.

## Ví dụ
Sơ yếu lý lịch của tôi: Bằng cử nhân Khoa học Máy tính với kinh nghiệm về Python.
Câu hỏi: Bạn có kinh nghiệm với Python không?
Có, tôi có kinh nghiệm với Python.

Chi tiết giáo dục: {resume_section}
Câu hỏi: {question}
"""

# Mẫu chi tiết kinh nghiệm
experience_details_template = """
Trả lời câu hỏi sau dựa trên chi tiết kinh nghiệm được cung cấp.

## Quy tắc
- Trả lời câu hỏi trực tiếp.
- Nếu có vẻ như bạn có kinh nghiệm, ngay cả khi không được định nghĩa rõ ràng, hãy trả lời như thể bạn có kinh nghiệm.
- Nếu không chắc chắn, hãy trả lời "Tôi không có kinh nghiệm về điều đó, nhưng tôi học nhanh" hoặc "Chưa, nhưng sẵn sàng học hỏi."
- Giữ câu trả lời dưới 140 ký tự.

## Ví dụ
Sơ yếu lý lịch của tôi: 3 năm làm nhà phát triển phần mềm với kinh nghiệm lãnh đạo.
Câu hỏi: Bạn có kinh nghiệm lãnh đạo không?
Có, tôi có 3 năm kinh nghiệm lãnh đạo.

Chi tiết kinh nghiệm: {resume_section}
Câu hỏi: {question}
"""

# Mẫu dự án
projects_template = """
Trả lời câu hỏi sau dựa trên chi tiết dự án được cung cấp.

## Quy tắc
- Trả lời câu hỏi trực tiếp.
- Nếu có vẻ như bạn có kinh nghiệm, ngay cả khi không được định nghĩa rõ ràng, hãy trả lời như thể bạn có kinh nghiệm.
- Giữ câu trả lời dưới 140 ký tự.

## Ví dụ
Sơ yếu lý lịch của tôi: Dẫn dắt việc phát triển một ứng dụng di động, có sẵn kho lưu trữ.
Câu hỏi: Bạn đã từng dẫn dắt dự án nào chưa?
Có, đã dẫn dắt việc phát triển một ứng dụng di động

Dự án: {resume_section}
Câu hỏi: {question}
"""

# Mẫu tính khả dụng
availability_template = """
Trả lời câu hỏi sau dựa trên chi tiết tính khả dụng được cung cấp.

## Quy tắc
- Trả lời câu hỏi trực tiếp.
- Giữ câu trả lời dưới 140 ký tự.
- Chỉ sử dụng dấu chấm nếu câu trả lời có nhiều câu.

## Ví dụ
Sơ yếu lý lịch của tôi: Có thể bắt đầu ngay lập tức.
Câu hỏi: Khi nào bạn có thể bắt đầu?
Tôi có thể bắt đầu ngay lập tức.

Tính khả dụng: {resume_section}
Câu hỏi: {question}
"""

# Mẫu kỳ vọng lương
salary_expectations_template = """
Trả lời câu hỏi sau dựa trên kỳ vọng lương được cung cấp.

## Quy tắc
- Trả lời câu hỏi trực tiếp.
- Giữ câu trả lời dưới 140 ký tự.
- Chỉ sử dụng dấu chấm nếu câu trả lời có nhiều câu.

## Ví dụ
Sơ yếu lý lịch của tôi: Đang tìm kiếm mức lương trong khoảng 50k-60k USD.
Câu hỏi: Kỳ vọng lương của bạn là gì?
55000.

Kỳ vọng lương: {resume_section}
Câu hỏi: {question}
"""

# Mẫu chứng chỉ
certifications_template = """
Trả lời câu hỏi sau dựa trên chứng chỉ được cung cấp.

## Quy tắc
- Trả lời câu hỏi trực tiếp.
- Nếu có vẻ như bạn có kinh nghiệm, ngay cả khi không được định nghĩa rõ ràng, hãy trả lời như thể bạn có kinh nghiệm.
- Nếu không chắc chắn, hãy trả lời "Tôi không có kinh nghiệm về điều đó, nhưng tôi học nhanh" hoặc "Chưa, nhưng sẵn sàng học hỏi."
- Giữ câu trả lời dưới 140 ký tự.

## Ví dụ
Sơ yếu lý lịch của tôi: Được chứng nhận Quản lý Dự án Chuyên nghiệp (PMP).
Câu hỏi: Bạn có chứng chỉ PMP không?
Có, tôi được chứng nhận PMP.

Chứng chỉ: {resume_section}
Câu hỏi: {question}
"""

# Mẫu ngôn ngữ
languages_template = """
Trả lời câu hỏi sau dựa trên kỹ năng ngôn ngữ được cung cấp.

## Quy tắc
- Trả lời câu hỏi trực tiếp.
- Nếu có vẻ như bạn có kinh nghiệm, ngay cả khi không được định nghĩa rõ ràng, hãy trả lời như thể bạn có kinh nghiệm.
- Nếu không chắc chắn, hãy trả lời "Tôi không có kinh nghiệm về điều đó, nhưng tôi học nhanh" hoặc "Chưa, nhưng sẵn sàng học hỏi."
- Giữ câu trả lời dưới 140 ký tự. Không thêm bất kỳ ngôn ngữ nào không có trong kinh nghiệm của tôi

## Ví dụ
Sơ yếu lý lịch của tôi: Thông thạo tiếng Ý và tiếng Anh.
Câu hỏi: Bạn nói những ngôn ngữ nào?
Thông thạo tiếng Ý và tiếng Anh.

Ngôn ngữ: {resume_section}
Câu hỏi: {question}
"""

# Mẫu sở thích
interests_template = """
Trả lời câu hỏi sau dựa trên sở thích được cung cấp.

## Quy tắc
- Trả lời câu hỏi trực tiếp.
- Giữ câu trả lời dưới 140 ký tự.
- Chỉ sử dụng dấu chấm nếu câu trả lời có nhiều câu.

## Ví dụ
Sơ yếu lý lịch của tôi: Quan tâm đến AI và khoa học dữ liệu.
Câu hỏi: Sở thích của bạn là gì?
AI và khoa học dữ liệu.

Sở thích: {resume_section}
Câu hỏi: {question}
"""

# Mẫu tóm tắt mô tả công việc
summarize_prompt_template = """
Với tư cách là một chuyên gia HR giàu kinh nghiệm, nhiệm vụ của bạn là xác định và phác thảo các kỹ năng và yêu cầu chính cần thiết cho vị trí công việc này. 
Sử dụng mô tả công việc được cung cấp làm đầu vào để trích xuất tất cả thông tin liên quan. 
Điều này sẽ liên quan đến việc phân tích kỹ lưỡng trách nhiệm công việc và tiêu chuẩn ngành. 
Bạn nên xem xét cả kỹ năng kỹ thuật và kỹ năng mềm cần thiết để xuất sắc trong vai trò này. 
Ngoài ra, hãy chỉ rõ bất kỳ bằng cấp, chứng chỉ hoặc kinh nghiệm nào là cần thiết. 
Phân tích của bạn cũng nên phản ánh bản chất phát triển của vai trò này, xem xét xu hướng tương lai và cách chúng có thể ảnh hưởng đến các năng lực cần thiết.

Quy tắc:
Loại bỏ văn bản mẫu
Chỉ bao gồm thông tin liên quan để so sánh mô tả công việc với sơ yếu lý lịch

# Yêu cầu phân tích
Phân tích của bạn nên bao gồm các phần sau:
Kỹ năng kỹ thuật: Liệt kê tất cả các kỹ năng kỹ thuật cụ thể cần thiết cho vai trò dựa trên trách nhiệm được mô tả trong mô tả công việc.
Kỹ năng mềm: Xác định các kỹ năng mềm cần thiết, chẳng hạn như khả năng giao tiếp, giải quyết vấn đề, quản lý thời gian, v.v.
Bằng cấp và Chứng chỉ: Chỉ rõ các bằng cấp và chứng chỉ cần thiết cho vai trò.
Kinh nghiệm chuyên môn: Mô tả các kinh nghiệm làm việc liên quan được yêu cầu hoặc ưu tiên.
Sự phát triển của vai trò: Phân tích cách vai trò có thể phát triển trong tương lai, xem xét xu hướng ngành và cách chúng có thể ảnh hưởng đến các kỹ năng cần thiết.

# Kết quả cuối cùng:
Phân tích của bạn nên được cấu trúc trong một tài liệu rõ ràng và có tổ chức với các phần riêng biệt cho mỗi điểm được liệt kê ở trên. Mỗi phần nên chứa:
Tổng quan toàn diện này sẽ đóng vai trò như một hướng dẫn cho quá trình tuyển dụng, đảm bảo xác định được các ứng viên có trình độ cao nhất.

# Mô tả công việc:
```
{text}
```

---

# Tóm tắt mô tả công việc"""

# Mẫu thư xin việc
coverletter_template = """
# Soạn thảo một bức thư xin việc ngắn gọn và ấn tượng dựa trên mô tả công việc và sơ yếu lý lịch được cung cấp. 
# Bức thư không nên dài quá ba đoạn và nên được viết theo phong cách chuyên nghiệp nhưng gần gũi. 
# Tránh sử dụng bất kỳ chỗ trống nào và đảm bảo rằng bức thư chảy tự nhiên và được điều chỉnh cho công việc.

# Phân tích mô tả công việc để xác định các tiêu chí và yêu cầu chính. 
# Giới thiệu ngắn gọn về ứng viên, liên kết mục tiêu nghề nghiệp của họ với vai trò. 
# Nêu bật các kỹ năng và kinh nghiệm liên quan từ sơ yếu lý lịch mà phù hợp trực tiếp với yêu cầu của công việc, 
# sử dụng các ví dụ cụ thể để minh họa những tiêu chí này. 
# Tham chiếu đến các khía cạnh nổi bật của công ty, chẳng hạn như sứ mệnh hoặc giá trị, 
# mà ứng viên cảm thấy phù hợp với mục tiêu nghề nghiệp của họ. 
# Kết thúc bằng một tuyên bố mạnh mẽ về lý do tại sao ứng viên là sự phù hợp tốt cho vị trí, 
# thể hiện mong muốn thảo luận thêm.

# Vui lòng viết bức thư xin việc theo cách trực tiếp đề cập đến vai trò công việc và đặc điểm của công ty, 
# đảm bảo rằng nó vẫn ngắn gọn và hấp dẫn mà không có những trang trí không cần thiết. 
# Bức thư nên được định dạng thành các đoạn và không bao gồm lời chào hoặc chữ ký.

## Quy tắc:
# - Chỉ cung cấp văn bản của bức thư xin việc.
# - Không bao gồm bất kỳ lời giới thiệu, giải thích hoặc thông tin bổ sung nào.
# - Bức thư nên được định dạng thành các đoạn.

## Mô tả công việc:
```
{job_description}
```
## Sơ yếu lý lịch của tôi:
```
{resume}
```
"""

# Mẫu câu hỏi số cho phép đọc kỹ sơ yếu lý lịch và trả lời các câu hỏi cụ thể liên quan đến kinh nghiệm của ứng viên với số năm.
numeric_question_template = """
Đọc kỹ sơ yếu lý lịch sau và trả lời các câu hỏi cụ thể liên quan đến kinh nghiệm của ứng viên với số năm. Làm theo các hướng dẫn chiến lược này khi phản hồi:

1. **Kinh nghiệm liên quan và suy luận:**
   - **Công nghệ tương tự:** Nếu kinh nghiệm với một công nghệ cụ thể không được nêu rõ, nhưng ứng viên có kinh nghiệm với các công nghệ tương tự hoặc liên quan, hãy cung cấp một số năm hợp lý phản ánh kinh nghiệm liên quan này. Ví dụ, nếu ứng viên có kinh nghiệm với Python và các dự án liên quan đến các công nghệ tương tự như Java, hãy ước lượng một số năm hợp lý cho Java.
   - **Dự án và nghiên cứu:** Xem xét các dự án và nghiên cứu của ứng viên để suy luận các kỹ năng không được nêu rõ. Các dự án phức tạp và tiên tiến thường chỉ ra chuyên môn sâu hơn.

2. **Kinh nghiệm gián tiếp và nền tảng học vấn:**
   - **Loại trường đại học và ngành học:** Xem xét loại trường đại học và khóa học đã theo học.
   - **Điểm thi:** Xem xét điểm thi đạt được. Điểm cao trong các môn học liên quan có thể chỉ ra khả năng và hiểu biết mạnh mẽ hơn.
   - **Luận văn liên quan:** Xem xét luận văn mà ứng viên đã thực hiện. Các dự án tiên tiến gợi ý kỹ năng sâu hơn.
   - **Vai trò và trách nhiệm:** Đánh giá các vai trò và trách nhiệm đã đảm nhận để ước lượng kinh nghiệm với các công nghệ hoặc kỹ năng cụ thể.

3. **Ước lượng kinh nghiệm:**
   - **Không có kinh nghiệm bằng 0:** Phản hồi "0" là hoàn toàn bị cấm. Nếu không thể xác nhận kinh nghiệm trực tiếp, hãy cung cấp tối thiểu "2" năm dựa trên kinh nghiệm suy luận hoặc liên quan.
   - **Đối với kinh nghiệm thấp (tối đa 5 năm):** Ước lượng kinh nghiệm dựa trên bằng cấp, kỹ năng và dự án đã thực hiện, luôn cung cấp ít nhất "2" năm khi có liên quan.
   - **Đối với kinh nghiệm cao:** Đối với các mức độ kinh nghiệm cao, hãy cung cấp một số dựa trên bằng chứng rõ ràng từ sơ yếu lý lịch. Tránh đưa ra suy luận cho các mức độ kinh nghiệm cao trừ khi bằng chứng là mạnh mẽ.

4. **Quy tắc:**
   - Trả lời câu hỏi trực tiếp bằng một số, tránh hoàn toàn "0".

## Ví dụ 1
```
## Chương trình học

# Đã có bằng cử nhân ngành khoa học máy tính. 
# Tôi đã làm việc trong nhiều năm với giao thức MQTT.

## Câu hỏi

# Bạn có bao nhiêu năm kinh nghiệm với IoT?

## Câu trả lời

# 4
```
## Ví dụ 1
```
## Chương trình học

Tôi đã có bằng cử nhân ngành khoa học máy tính.

## Câu hỏi

Bạn có bao nhiêu năm kinh nghiệm với Bash?

## Câu trả lời

5
```

## Ví dụ 2
```
## Chương trình học

Tôi là một kỹ sư phần mềm với 10 năm kinh nghiệm trong Java và Python. Tôi đã làm việc trên một dự án AI.

## Câu hỏi

Bạn có bao nhiêu năm kinh nghiệm với AI?

## Câu trả lời

5
```

## Sơ yếu lý lịch:
```
{resume_educations}
{resume_jobs}
{resume_projects}
```
        
## Câu hỏi:
{question}

---

Khi trả lời, hãy xem xét tất cả thông tin có sẵn, bao gồm các dự án, kinh nghiệm làm việc và nền tảng học thuật, để cung cấp một câu trả lời chính xác và hợp lý. Hãy nỗ lực hết mình để suy luận kinh nghiệm liên quan và tránh mặc định về 0 nếu có thể ước lượng bất kỳ kinh nghiệm liên quan nào.

"""

options_template = """Dưới đây là một sơ yếu lý lịch và một câu hỏi đã được trả lời về sơ yếu lý lịch, câu trả lời là một trong các tùy chọn.

## Quy tắc
- Không bao giờ chọn tùy chọn mặc định/đặt chỗ, ví dụ: 'Chọn một tùy chọn', 'Không có', 'Chọn từ các tùy chọn bên dưới', v.v.
- Câu trả lời phải là một trong các tùy chọn.
- Câu trả lời phải chỉ chứa một trong các tùy chọn.

## Ví dụ
Sơ yếu lý lịch của tôi: Tôi là một kỹ sư phần mềm với 10 năm kinh nghiệm về swift, python, C, C++.
Câu hỏi: Bạn có bao nhiêu năm kinh nghiệm với python?
Tùy chọn: [1-2, 3-5, 6-10, 10+]
10+

-----

## Sơ yếu lý lịch của tôi:
```
{resume}
```

## Câu hỏi:
{question}

## Tùy chọn:
{options}

## """

try_to_fix_template = """\
Mục tiêu là sửa đổi văn bản của một trường nhập liệu trên một trang web.

## Quy tắc
- Sử dụng lỗi để sửa văn bản gốc.
- Lỗi "Vui lòng nhập một câu trả lời hợp lệ" thường có nghĩa là văn bản quá dài, hãy rút ngắn câu trả lời xuống dưới 1 tweet.
- Đối với các lỗi như "Nhập một số nguyên giữa 3 và 30", chỉ cần một số.

-----

## Câu hỏi của biểu mẫu
{question}

## Nhập
{input} 

## Lỗi
{error}  

## Đầu vào đã sửa
"""

func_summarize_prompt_template = """
        Dưới đây là hai văn bản, một văn bản có các chỗ giữ chỗ và một văn bản không có, văn bản thứ hai sử dụng thông tin từ văn bản đầu tiên để điền vào các chỗ giữ chỗ.
        
        ## Quy tắc
        - Một chỗ giữ chỗ là một chuỗi như "[[chỗ giữ chỗ]]". Ví dụ: "[[công_ty]]", "[[chức_vụ]]", "[[số_năm_kinh_nghiệm]]"...
        - Nhiệm vụ là loại bỏ các chỗ giữ chỗ khỏi văn bản.
        - Nếu không có thông tin để điền vào một chỗ giữ chỗ, hãy loại bỏ chỗ giữ chỗ và điều chỉnh văn bản cho phù hợp.
        - Không có chỗ giữ chỗ nào nên còn lại trong văn bản.
        
        ## Ví dụ
        Văn bản có chỗ giữ chỗ: "Tôi là một kỹ sư phần mềm với 10 năm kinh nghiệm về [chỗ giữ chỗ] và [chỗ giữ chỗ]."
        Văn bản không có chỗ giữ chỗ: "Tôi là một kỹ sư phần mềm với 10 năm kinh nghiệm."
        
        -----
        
        ## Văn bản có chỗ giữ chỗ:
        {text_with_placeholders}
        
        ## Văn bản không có chỗ giữ chỗ:"""
