// -----------------------------
// 画像プレビュー（index.html用）
// -----------------------------
document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.querySelector('input[type="file"]');
    const previewBox = document.querySelector(".image-preview img");

    if (fileInput && previewBox) {
        fileInput.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (!file) return;

            // 画像以外は無視
            if (!file.type.startsWith("image/")) {
                alert("画像ファイルを選んでください。");
                return;
            }

            const reader = new FileReader();
            reader.onload = function (event) {
                previewBox.src = event.target.result;
                previewBox.style.display = "block";
            };
            reader.readAsDataURL(file);
        });
    }

    // -----------------------------------
    // フォーム送信時のローディング表示
    // -----------------------------------
    const form = document.querySelector("form");
    const loading = document.querySelector("#loading");

    if (form && loading) {
        form.addEventListener("submit", () => {
            loading.style.display = "flex";
        });
    }

    // -----------------------------------
    // ボタンアニメーション（軽い演出）
    // -----------------------------------
    const buttons = document.querySelectorAll("button, .btn-submit, .btn-download");
    buttons.forEach(btn => {
        btn.addEventListener("mousedown", () => {
            btn.style.transform = "scale(0.96)";
        });
        btn.addEventListener("mouseup", () => {
            btn.style.transform = "scale(1)";
        });
        btn.addEventListener("mouseleave", () => {
            btn.style.transform = "scale(1)";
        });
    });
});
