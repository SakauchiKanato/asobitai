// -----------------------------
// 画像プレビュー（index.html用）
// -----------------------------
document.addEventListener("DOMContentLoaded", () => {
    // 採点前の画像プレビュー
    const fileInput1 = document.querySelector('#imageFile');
    const previewBox1 = document.querySelector("#previewImg1");

    if (fileInput1 && previewBox1) {
        fileInput1.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (!file) return;

            // 画像以外は無視
            if (!file.type.startsWith("image/")) {
                alert("画像ファイルを選んでください。");
                return;
            }

            const reader = new FileReader();
            reader.onload = function (event) {
                previewBox1.src = event.target.result;
                previewBox1.style.display = "block";
            };
            reader.readAsDataURL(file);
        });
    }

    // 採点後の画像プレビュー
    const fileInput2 = document.querySelector('#imageFile2');
    const previewBox2 = document.querySelector("#previewImg2");

    if (fileInput2 && previewBox2) {
        fileInput2.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (!file) return;

            // 画像以外は無視
            if (!file.type.startsWith("image/")) {
                alert("画像ファイルを選んでください。");
                return;
            }

            const reader = new FileReader();
            reader.onload = function (event) {
                previewBox2.src = event.target.result;
                previewBox2.style.display = "block";
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
