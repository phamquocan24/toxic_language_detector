document.querySelectorAll('.clickable-row').forEach(row => {
    row.addEventListener('click', () => {
        const id = row.querySelector('.select-row').value;
        window.location.href = `/admin/brands/edit`;
    });
});
