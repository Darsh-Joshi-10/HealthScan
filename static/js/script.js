document.getElementById("xray").addEventListener("change", function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(event) {
            const previewImage = document.getElementById("preview");
            previewImage.src = event.target.result;
            previewImage.style.display = "block";
        };
        reader.readAsDataURL(file);
    }
});
