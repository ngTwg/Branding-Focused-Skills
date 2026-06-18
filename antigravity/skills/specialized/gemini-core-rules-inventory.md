# 📚 GEMINI CORE RULES INVENTORY (LEGACY & BEHAVIORAL DETAILS)

> **MỤC ĐÍCH:** Lưu trữ các rules phụ, hướng dẫn hành vi chi tiết, và danh mục MCP phụ để tối ưu hóa bộ nhớ boot của file governance chính.

---

## 🛠️ RULE 14: CODING DISCIPLINE (Behavioral Guidelines)

> Tradeoff: Các nguyên tắc này bias toward caution over speed. Với trivial tasks, dùng judgment.

### 14A. Think Before Coding
**KHÔNG** assume, **KHÔNG** hide confusion. Surface tradeoffs TRƯỚC khi implement.
- State assumptions explicitly. Nếu uncertain → hỏi ngay.
- Nếu có nhiều cách hiểu → trình bày tất cả, KHÔNG tự chọn silently.
- Nếu có approach đơn giản hơn → nói rõ. Push back khi có lý do.
- Nếu unclear → STOP. Đặt tên cụ thể điểm confusing. Hỏi.

### 14B. Simplicity First
**Minimum code** giải quyết đúng vấn đề. Không speculative.
- ❌ Không thêm features ngoài yêu cầu.
- ❌ Không abstraction cho single-use code.
- ❌ Không "flexibility/configurability" nếu không được yêu cầu.
- ❌ Không error handling cho impossible scenarios.
- ✅ Nếu viết 200 dòng mà có thể 50 → rewrite.
- **Self-check:** "Senior engineer có nói đây overcomplicated không?" → Nếu có → simplify.

### 14C. Surgical Changes & AST Range-Reads
**Chạm chỉ những gì cần thiết. Tiết kiệm tối đa Token khi đọc/viết.**
Khi kiểm tra hoặc chỉnh sửa existing code:
- **Prioritize AST structure:** Sử dụng AST Analyzer hoặc grep để xem trước cấu trúc lớp, hàm thay vì dùng `view_file` toàn bộ nội dung.
- **Range-Limited Reads:** Bắt buộc sử dụng các tham số `StartLine` và `EndLine` trong công cụ `view_file` để chỉ đọc đúng vùng code cần xử lý. Nghiêm cấm đọc cả file >200 dòng không giới hạn dòng.
- ❌ Không "improve" adjacent code, comments, formatting không liên quan.
- ❌ Không refactor những gì không broken.
- ✅ Match existing style, dù bạn làm khác đi.
- ✅ Nếu thấy dead code không liên quan → mention, KHÔNG xóa.

Khi changes tạo orphans:
- ✅ Remove imports/variables/functions mà CHANGES CỦA BẠN làm unused.
- ❌ Không xóa pre-existing dead code trừ khi được yêu cầu.

**Test:** Mỗi changed line phải trace trực tiếp từ user request.

### 14D. Goal-Driven Execution
**Define success criteria. Loop until verified.**
Transform tasks thành verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

Với multi-step tasks, state brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

### 14E. Self-Audit Before Completion
**LUÔN audit lại code vừa viết TRƯỚC KHI báo cáo hoàn thành.**
- Nếu bạn vừa viết một block code 200 dòng, hãy review lại xem có cách nào viết ngắn gọn, logic gọn gàng hơn trong 50 dòng hay không. Nếu có → Rewrite ngay lập tức.
- Review kỹ các thay đổi so với file gốc để chắc chắn không để lại "dead code", không gây side-effect.
- Không vội vàng kết thúc task nếu chưa chạy Self-Audit.

---

## 🔌 RULE 15: MCP ECOSYSTEM REGISTRY

> Danh sách MCP servers đã được verify và cấu hình cho project. Dùng `npx` — không cần global install.

### 15A. Installed / Configured MCP Servers

| Server | Package | Dùng cho |
| :--- | :--- | :--- |
| **Playwright MCP** | `npx @playwright/mcp@latest` | Browser automation. Repo: [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) |
| **Composio MCP** | `npx -y @composio/mcp` | 500+ integrations. Trang chính: [composio.dev](https://composio.dev) |
| **MCP Servers (Official)** | `github.com/modelcontextprotocol/servers` | Nền tảng gốc: [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) |

**Playwright MCP config:**
```json
{ "mcpServers": { "playwright": { "command": "npx", "args": ["@playwright/mcp@latest"] } } }
```

**Composio MCP config:**
```json
{ "mcpServers": { "composio": { "command": "npx", "args": ["-y", "@composio/mcp"], "env": { "COMPOSIO_API_KEY": "<key>" } } } }
```

### 15B. Reference Repos (Knowledge / Not installed)

| Repo | Status | Ghi chú |
| :--- | :--- | :--- |
| `bytedance/UI-TARS-desktop` | ✅ Verified | Multimodal AI Agent stack, desktop app |
| `rohitg00/agentmemory` | ✅ Verified | Persistent memory cho AI coding agents |
| `datawhalechina/hello-agents` | ✅ Verified | Tutorial xây dựng agent từ zero (tiếng Trung) |
| `datawhalechina/easy-vibe` | ✅ Verified | [github.com/datawhalechina/easy-vibe](https://github.com/datawhalechina/easy-vibe) |
| `HKUDS/AI-Trader` | ✅ Verified | [github.com/HKUDS/AI-Trader](https://github.com/HKUDS/AI-Trader) |
| `addyosmani/agent-skills` | ✅ Verified | [github.com/addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) |
| `mattpocock/skills` | ✅ Verified | [github.com/mattpocock/skills](https://github.com/mattpocock/skills) |
| `obra/superpowers` | ✅ Verified | [github.com/obra/superpowers](https://github.com/obra/superpowers) |
| `github/spec-kit` | ✅ Verified | [github.com/github/spec-kit](https://github.com/github/spec-kit) |
| `millionco/react-doctor` | ✅ Verified | [github.com/millionco/react-doctor](https://github.com/millionco/react-doctor) |
| `anthropics/financial-services` | ✅ Verified | [github.com/anthropics/financial-services](https://github.com/anthropics/financial-services) |

### 15C. NOT Installable on Windows

| Tool | Lý do |
| :--- | :--- |
| `Z4nzu/hackingtool` | ❌ Linux-only (Bash + Kali deps). Dùng qua WSL hoặc Docker nếu cần. |

---

## 🛡️ RULE 19: SECURE MCP & THIRD-PARTY SKILLS FIREWALL

> **MỤC TIÊU:** Ngăn chặn tuyệt đối các cuộc tấn công gián tiếp (Indirect Prompt Injection), tấn công chuỗi cung ứng (Supply Chain Attacks), và thoát vùng giam giữ (Path Traversal) khi chạy các MCP Filesystem cục bộ.

### 19A. Nguyên Tắc Cài Đặt MCP
- **Zero dynamic updates:** Nghiêm cấm sử dụng phiên bản `@latest` hoặc cài đặt động không chỉ định rõ version cho các gói thư viện/server từ bên thứ ba.
- **Audit before use:** Trước khi cấu hình bất kỳ MCP server mới nào vào IDE hoặc Client, bắt buộc thực hiện kiểm tra mã nguồn và chạy `npm audit` hoặc quét lỗ hổng phụ thuộc.

### 19B. Giao Thức Bảo Mật File System MCP
- **Strict path confinement:** Mọi Filesystem MCP server phải được giới hạn cứng (Hard-lock) tại thư mục làm việc của dự án (`C:\ProJect\QUIZVLU`).
- **Path Traversal Shield:** Bắt buộc sử dụng bộ lọc bảo mật hoặc proxy trung gian (ví dụ: `tools/secure_mcp_proxy.py`) để quét và ngăn chặn tức thì mọi yêu cầu chứa ký tự dịch chuyển thư mục như `..` hoặc symlink trỏ ra phân vùng nhạy cảm ngoài dự án (`~/.ssh`, `~/.aws`, `.env`).
- **Read-Only Default:** Ưu tiên khởi chạy MCP ở chế độ chỉ đọc nếu tác vụ của AI Client chỉ là đọc và phân tích mã nguồn.

### 19C. Nhật Ký Kiểm Toán (Auditing)
- Luôn ghi chép toàn bộ các thao tác gọi công cụ, đường dẫn đích và trạng thái phản hồi vào file nhật ký cục bộ (`mcp_security_audit.log`) để phục vụ rà soát thủ công khi cần thiết.

---

## 📊 RULE 20: OBSERVABILITY (mở rộng từ 19C)
> Chuẩn hóa logging cho cả tác vụ non-security, không chỉ MCP.
- Mỗi **destructive action** (xóa/ghi đè/migration) log: timestamp + file đích + lý do.
- Tier 3+ log thêm: tier classification + danh sách inventory đã load.
- Log cục bộ, không chứa secret (tuân Rule 18A).

---

## GHI CHÚ HỢP NHẤT (v7.3.0)
- Block "CLAUDE.md Behavioral Guidelines" cũ đã gỡ khỏi file boot — nội dung trùng 100% với Rule 14 (14A–14E). Rule 14 là source of truth duy nhất cho coding discipline.
