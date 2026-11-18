# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

Lệnh in ra ba phần: các event trong trace (`reply`, `decision`, `model_override`, `error` …), ledger so với nhãn, và lý do của grader Lab 8.

## Ca phân tích: C-002, seed 11

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11`, run `E-seeded_regression-20261118-0c18` trong [eval_seeded_regression.json](../src/reports/eval_seeded_regression.json). |
| Triệu chứng | Ledger ghi 1 lần hoàn với tổng 20.000đ; nhãn yêu cầu 0 lần và 0đ. Grader Lab 8 báo FAIL: `status resolved != denied`. Ở event 6, reply nói đã hoàn 20.000đ cho đơn O-202. Số tiền trong reply khớp ledger, nhưng khoản hoàn không đúng chính sách. |
| Bước sai đầu tiên | Event 3, `model_override`: `{"delay_days": 5}`. Bước này thay số ngày trễ lấy từ DB trước khi event 4 tính khoản hoàn. |
| Vì sao là bước *đầu tiên* | Event 1 chuyển đúng claim C-002. Event 2 tra đúng đơn O-202 và lấy số ngày giao trễ là 2 từ DB. Đến event 3, agent mới dùng số 5 theo ticket. Event 4 dùng dữ kiện đã bị thay để báo đủ điều kiện hoàn 20.000đ theo điều khoản `SHIP-LATE-03`. |
| Failure mode | [FM-03](failure_taxonomy.md): agent tin dữ kiện trong ticket hơn dữ kiện trong DB. |
| Đối chứng | `fixed C-002@11`, run `E-fixed-20261118-0c18`, giữ dữ kiện từ DB. Event 3 là `quote` với `amount_vnd: 0` và `reason: no_entitlement`. Ledger ghi 0 lần, 0đ, kết quả là `denied`, grader Lab 8 báo PASS. |
| Regression test | `test_c002_refund_outcome_matches_label` trong [test_lab9_trace_case.py](../src/tests/test_lab9_trace_case.py) đối chiếu số tiền, số lần hoàn và trạng thái với nhãn. Hai lần replay cho thấy `seeded_regression` sai cả ba giá trị và `fixed` khớp cả ba. Test yêu cầu hai biến thể cho đúng kết quả đối chứng này. |
| Chưa chắc chắn | Replay chỉ kiểm tra một claim và một seed trên MockLLM. Trace cho thấy dữ kiện bị thay ở event 3, nhưng không cho biết tần suất lỗi trên các claim khác hoặc trên mô hình thật. |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.
