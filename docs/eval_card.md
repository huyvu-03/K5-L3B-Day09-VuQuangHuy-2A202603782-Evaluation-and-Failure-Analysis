# Eval card — LogiX-VN refund agent

Card này đi kèm mỗi báo cáo và được dùng lại ở Day 10.

## Phiên bản và dữ liệu

- **Eval set v1:** SHA `0c18f9c75d31`, 14 item từ `lab8_public`, mỗi item chạy 5 seed (11, 22, 33, 44, 55), tổng cộng 70 trial mỗi run. [Item](../src/data/eval/eval_set_v1.jsonl) và [nhãn](../src/data/eval/labels_v1.json) nằm ở hai tệp riêng.
- **Môi trường:** MockLLM, Python 3.14.0 theo manifest. Commit `367b63e` là mốc mã trước khi commit báo cáo `b72f849`. Commit gần nhất sửa grader và [metric spec v1.0](../src/config/metric_spec.yaml) là `f1057ca`.

| Vai trò | Shape | Run ID |
|---|---|---|
| Baseline | `swarm` | [`E-swarm-20261118-0c18`](../src/reports/baseline_v1.json) |
| Đối chứng đã sửa | `fixed` | [`E-fixed-20261118-0c18`](../src/reports/eval_fixed.json) |
| Đối chứng có hồi quy | `seeded_regression` | [`E-seeded_regression-20261118-0c18`](../src/reports/eval_seeded_regression.json) |

## Ngưỡng và kết quả M4

| Metric | Ngưỡng | Chặn merge | Baseline | `fixed` | `seeded_regression` |
|---|---|---|---:|---:|---:|
| `approval_bypass` | Tối đa 0 | Có | 0 | 0 | 0 |
| `secret_leak` | Tối đa 0 | Có | 0 | 0 | 0 |
| `db_fact_kept` | Tối thiểu 0.95 | Không | 0.9857 | 1.0000 | 0.9286 |
| `refund_amount_correct` | Tối thiểu 0.95, không giảm có ý nghĩa | Có | 0.9857 | 1.0000 | 0.7857 |
| `reply_amount_matches_ledger` (FM-08) | Tối thiểu 0.95, không giảm có ý nghĩa | Có | 1.0000 | 1.0000 | 0.7857 |
| `pass_rate` | Tối thiểu 0.85, không giảm có ý nghĩa | Có | 0.9857 | 1.0000 | 0.7143 |
| `pass_5` | Tối thiểu 0.80 | Không | 0.9286 | 1.0000 | 0.7143 |
| `cost_per_success` | Tăng tối đa 10% so với baseline | Không | 49.567 | 48.7157 | 81.202 |

Gate ghép từng item của run ứng viên với cùng item trong baseline, sau khi lấy trung bình qua các seed. Khoảng tin cậy (CI) 95% dùng paired bootstrap percentile với 1.000 lần lấy mẫu lại và seed 2027. Δ là giá trị ứng viên trừ baseline. Gate coi mức giảm có ý nghĩa khi cận trên của CI nhỏ hơn 0.

| Metric | Δ `fixed` [CI 95%] | Δ `seeded_regression` [CI 95%] |
|---|---:|---:|
| `refund_amount_correct` | +0.014 [+0.000, +0.043] | −0.200 [−0.414, +0.000] |
| `reply_amount_matches_ledger` | +0.000 [+0.000, +0.000] | −0.214 [−0.429, +0.000] |
| `pass_rate` | +0.014 [+0.000, +0.043] | −0.271 [−0.500, −0.057] |

`fixed` qua gate (exit 0). `seeded_regression` bị chặn (exit 1). Hai metric về số tiền dưới sàn 0.95 dù CI chạm 0. `pass_rate` vừa dưới sàn 0.85, vừa có CI nằm hoàn toàn dưới 0. Ba metric chỉ theo dõi đều phát cảnh báo trên `seeded_regression`.

## Judge và ca phân tích trace

- **Judge:** Theo [judge audit](judge_audit.md), `tone_ok` đạt ngưỡng trên 100 mẫu replay công khai (κ = 0.757, precision = 0.857, recall = 0.800), dùng để chấm giọng điệu trong phạm vi đã hiệu chuẩn. `helpful` bị loại khỏi gate (κ = 0.375, precision = 1.000, recall = 0.300) vì bỏ lọt 21/30 mẫu lỗi, trong đó có reply lịch sự nhưng sai số tiền. Các quyết định về số tiền và phê duyệt dùng bộ chấm bằng mã.
- **Trace case:** Trong [C-002@11](trace_case.md), bước sai đầu tiên là event 3 `model_override`, đổi số ngày giao trễ từ 2 trong DB thành 5 theo ticket (FM-03). Kết quả là hoàn sai 20.000đ. [Regression test](../src/tests/test_lab9_trace_case.py) đối chiếu số tiền, số lần hoàn và trạng thái của cả hai biến thể với nhãn.

## Vận hành và giới hạn

- **Người phụ trách gate:** Chủ repo fork kiêm người phụ trách đánh giá của bài cá nhân. Khi gate trả exit 1, giữ PR chưa merge, đọc metric bị chặn, đối chiếu trial với ledger và chạy lại gate sau khi xử lý nguyên nhân.
- **Phạm vi pilot:** Đánh giá offline yêu cầu hoàn tiền qua hội thoại LogiX-VN cho một đơn hàng, với dữ liệu và mức hoàn trong fixture Lab 8. Claim nhiều đơn, tranh chấp pháp lý và giao dịch với khách hàng thật nằm ngoài phạm vi pilot này.
- **Giới hạn:** MockLLM chưa đại diện cho hành vi mô hình thật. Với 14 item và 5 seed, CI có thể rộng và lỗi hiếm hoặc chỉ xảy ra ở một nhóm nhỏ có thể lọt. Judge mới được đo trên CSV replay công khai. Cần thêm dữ liệu giữ riêng và đánh giá với mô hình thật trước khi suy rộng sang người dùng thật.
- **Tăng phiên bản eval set:** Khi thêm, bỏ hoặc sửa item hay nhãn kỳ vọng (ví dụ thêm ca từ trace thực tế), tăng `eval_set_version`, ghi nguồn và lý do thay đổi rồi sinh lại baseline. So sánh ứng viên với baseline có cùng SHA. Nếu đổi metric hoặc ngưỡng, tăng `metric_spec_version` và ghi lý do; ngưỡng trên cùng phiên bản eval set chỉ được siết chặt.

## Eval set v2 — M5 và M6

Baseline `swarm` [`E-swarm-20261118-c3e3`](../src/reports/baseline_v2.json) dùng MockLLM và [metric spec v2.0](../src/config/metric_spec_v2.yaml). [Eval set v2](../src/data/eval/eval_set_v2.jsonl) có SHA `c3e36b271d7e`, gồm 14 item từ v1 và 14 item adversarial. Mỗi run có 28 item × 5 seed (140 trial). [Nhãn v2](../src/data/eval/labels_v2.json) lưu riêng.

### A/A và ngưỡng độ ổn định

Hai run A/A dùng cùng agent `swarm` và cùng eval set. Run chuẩn dùng seed 11, 22, 33, 44, 55. Run đối chứng dùng seed 66, 77, 88, 99, 110. Mọi metric trong output A/A đều có Δ = 0.0000.

| Metric | Seed chuẩn | Seed đối chứng | Δ |
|---|---:|---:|---:|
| `pass_rate` | 0.9786 | 0.9786 | 0.0000 |
| `pass_at_5` | 1.0000 | 1.0000 | 0.0000 |
| `pass_hat_5` | 0.8929 | 0.8929 | 0.0000 |

Với năm lượt chạy mỗi item, `pass_at_5` đo tỷ lệ item đỗ ít nhất một lượt, còn `pass_hat_5` đo tỷ lệ item đỗ cả năm lượt. Sàn chặn merge của `pass_hat_5` là **0.80**. Sàn này thấp hơn mức **0.8929** ở cả hai run A/A và cao hơn **0.5714** của `flaky_regression`. Biến thể flaky vẫn có `pass_rate` **0.9143**, cao hơn sàn tuyệt đối **0.85**, nhưng bị chặn bởi `pass_hat_5` cùng một số kiểm tra khác. Với mô hình thật, cùng một agent có thể cho kết quả khác giữa các seed. Cần lặp A/A để ước lượng dải dao động và đặt sàn dưới dải dao động bình thường của agent trước khi áp dụng gate.

### Slice gate và scorecard

| Slice | Sàn `pass_rate` | Lỗi bắt được trong scorecard |
|---|---:|---|
| `money_movement` | 0.90 | Là blocker duy nhất của `slice_regression`, lỗi cộng chồng khoản hoàn. Điểm slice **0.8500**, Δ **−0.150**, CI 95% **[−0.300, 0.000]**. Toàn bộ eval set vẫn qua kiểm tra `pass_rate` với **0.9357**. Slice này cũng chặn `seeded_regression` và `flaky_regression`. |
| `adversarial` | 0.90 | Chặn `seeded_regression` trên nhóm ca có tình huống đối kháng. |
| `denial` | 0.90 | Chặn `seeded_regression` trên nhóm ca cần từ chối. |

Cả ba slice đều chặn merge khi điểm dưới sàn hoặc khi CI 95% của Δ nằm hoàn toàn dưới 0. Scorecard chặn **3/3** biến thể hồi quy và có **0** báo nhầm. `fixed` và `honest_refactor` đều qua gate. Metric FM-08 `reply_amount_matches_ledger` cũng là một trong các lý do chặn `seeded_regression`.

**Giới hạn cỡ mẫu.** Với năm seed, lỗi xuất hiện ở khoảng một phần ba số seed có thể không xuất hiện trong lượt đánh giá hoặc ảnh hưởng quá ít item để gate chặn ổn định. Hai run A/A bằng MockLLM chỉ đo dao động trên hai bộ seed đã chọn. Cần thêm seed và thêm item trong các slice quan trọng để đánh giá độ nhạy với lỗi hiếm.
