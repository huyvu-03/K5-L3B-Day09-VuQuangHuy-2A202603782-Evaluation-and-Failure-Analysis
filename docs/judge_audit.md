# Judge audit — hiệu chuẩn judge bằng replay

Chạy các lệnh từ thư mục `src`:

```powershell
python -m lab9.judge --csv data/eval/judge_tone_public.csv --audit 5
python -m lab9.judge --csv data/eval/judge_helpful_public.csv --audit 5
```

## Kết quả hiệu chuẩn

| Tiêu chí | n | κ | Precision | Recall | Rogan–Gladen: lỗi quan sát → hiệu chỉnh | Đạt floors (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---:|---:|---:|---:|---|---|---|
| `tone_ok` | 100 | 0.757 | 0.857 | 0.800 | 0.28 → 0.30 | Có | Dùng được như tín hiệu chấm giọng điệu trong phạm vi replay này |
| `helpful` | 100 | 0.375 | 1.000 | 0.300 | 0.09 → 0.30 | Không | Không dùng làm release gate |

Quy ước: `FAIL` là lớp dương tính. Với `helpful`, precision 1.0 không đủ để dùng làm gate: judge chỉ bắt được 9/30 lỗi, bỏ lọt 21/30 lỗi (70%). Nhiều reply sai số tiền vẫn được judge cho PASS vì câu chữ nghe lịch sự hoặc có lời xin lỗi; kết quả hiệu chỉnh 0.30 chỉ ước lượng tỷ lệ lỗi tổng thể, không sửa các false pass của từng reply.

## Audit 5 bất đồng của `tone_ok`

Đối chiếu cột `note` trong `data/eval/judge_tone_public.csv`; các kết luận dưới đây dùng nhãn người làm ground truth cho bộ replay công khai.

| # | Case | Judge | Người | Ai đúng? | Ghi chú và điều chỉnh rubric |
|---:|---|---|---|---|---|
| 1 | H-008 | PASS | FAIL | Người | Reply xưng “em” và dùng “nha”, quá suồng sã với khách. Rubric cần chấm mức độ trang trọng theo quan hệ CS–khách, không xem từ thân mật là thân thiện mặc định. |
| 2 | H-017 | PASS | FAIL | Người | Dùng “bạn” và “nha” với khách lớn tuổi. Rubric cần yêu cầu cách xưng hô tôn trọng, phù hợp ngữ cảnh/độ tuổi. |
| 3 | H-029 | PASS | FAIL | Người | “Không cần nhắn thêm” mang giọng ra lệnh dù mở đầu bằng “Dạ, vui lòng”. Rubric cần đánh giá toàn câu; lời chào lịch sự không xóa được cách nói thiếu tôn trọng phía sau. |
| 4 | H-042 | FAIL | PASS | Người | Reply ngắn nhưng đủ ý; judge phạt vì thiếu lời xin lỗi. Rubric cần coi xin lỗi là tùy ngữ cảnh, không bắt buộc trong mọi câu trả lời đạt chuẩn. |
| 5 | H-051 | FAIL | PASS | Người | Từ “refund” được CS LogiX cho phép; judge phạt tiếng Anh quá cứng nhắc. Rubric cần cho phép từ vay mượn nằm trong danh sách được chấp thuận. |

## Vì sao loại `helpful` khỏi release gate

- Judge chỉ gắn FAIL cho 9 trong 30 mẫu mà người gắn FAIL; 21 lỗi còn lại bị cho PASS, nên gate sẽ để lọt phần lớn reply không hữu ích.
- Các ví dụ `HL-015`, `HL-016`, `HL-020` và `HL-028` sai số tiền so với ledger nhưng vẫn được judge cho PASS; judge đang phản ứng với văn phong lịch sự thay vì kiểm tra tính hữu ích theo bằng chứng.
- Precision 1.0 ở tập replay chỉ nói rằng không có false positive trong 100 mẫu này; recall 0.30 và κ 0.375 cho thấy độ bao phủ/đồng thuận không đạt chuẩn.
- Rogan–Gladen hiệu chỉnh tỷ lệ lỗi tổng thể về 0.30, nhưng không thể chỉ ra hoặc chặn các trường hợp sai riêng lẻ. Tiền phải được đối chiếu bằng grader code với ledger.

## Giới hạn

Hai judge được đánh giá trên CSV replay công khai, không phải tập held-out mới. Chỉ dùng `tone_ok` trong phạm vi đã hiệu chuẩn; không suy rộng kết quả này sang tính chính xác nghiệp vụ hay dùng LLM judge thay cho code grader về tiền và approval.
