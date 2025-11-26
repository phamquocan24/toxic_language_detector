<th style="max-width: 20px;">
    <div class="checkbox">
        <input type="checkbox" class="select-all" id="{{ $name ?? '' }}-select-all">
        <label for="{{ $name ?? '' }}-select-all"></label>
    </div>
</th>
<script>
    document.addEventListener("DOMContentLoaded", function () {
    // Xử lý chọn tất cả checkbox
        document.querySelector(".select-all").addEventListener("change", function () {
            let checkboxes = document.querySelectorAll("input[type='checkbox']:not(.select-all)");
            checkboxes.forEach(checkbox => checkbox.checked = this.checked);
        });

    // Xử lý khi bấm nút Delete
        document.querySelector(".btn-delete").addEventListener("click", function () {
            const selectedIds = [];
            document.querySelectorAll("input.select-row:checked").forEach(checkbox => {
                selectedIds.push(checkbox.value);
            });

            if (selectedIds.length === 0) {
                toastr.warning("Vui lòng chọn ít nhất một mục để xóa!");
                return;
            }

            const confirmationModal = document.querySelector("#confirmation-modal");
            confirmationModal.querySelector("#delete-ids").value = JSON.stringify(selectedIds);
            $(confirmationModal).modal('show');
        });

    });

    document.addEventListener("DOMContentLoaded", function () {
        const searchInput = document.querySelector('.dt-search input[type="search"]');
        const tableRows = document.querySelectorAll('tbody tr.clickable-row');

        // Gắn sự kiện lắng nghe
        searchInput.addEventListener("keyup", function () {
            const query = searchInput.value.toLowerCase();

            tableRows.forEach(row => {
                // Lấy giá trị ID và tên từ từng dòng
                const idCell = row.querySelector('td.dt-type-numeric');
                const nameCell = row.querySelector('a.name');

                // Kiểm tra có khớp không
                const matches = idCell.textContent.includes(query) || nameCell.textContent.toLowerCase().includes(query);

                // Hiển thị hoặc ẩn dòng dựa trên kết quả so khớp
                row.style.display = matches ? "" : "none";
            });
        });
    });
</script>
