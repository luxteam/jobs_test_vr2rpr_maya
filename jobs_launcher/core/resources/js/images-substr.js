function showImagesSubtraction(baselineId, renderId) {

    if (!($("#baselineImgPopup").attr('src') && $("#renderedImgPopup").attr('src'))) {
        infoBox("[Error] Can't read source image.", "#9b5e61");
        return;
    }

    var imagesTable = document.getElementById("imgsCompareTable");
    var diffTable = document.getElementById('imgsDiffTable');

    // if diff image is show now
    if (diffTable.style.display === "") {
        imagesTable.style.display = "";
        diffTable.style.display = "none";
        return;
    }

    renderCanvasData(baselineId, renderId, parseFloat(document.getElementById("thresholdRange").getAttribute('value')));

    imagesTable.style.display = "none";
    diffTable.style.display = "";
}

function renderCanvasData(baselineId, renderId, thresholdValue) {
    document.getElementById('thresholdRange').setAttribute("value", thresholdValue);
    var diffCanvas = document.getElementById('imgsDifferenceCanvas');

    var img1 = document.getElementById(baselineId);
    var img2 = document.getElementById(renderId);

    diffCanvas.width = img1.naturalWidth;
    diffCanvas.height = img1.naturalHeight;

    var ctx = diffCanvas.getContext("2d");
    ctx.clearRect(0, 0, diffCanvas.width, diffCanvas.height);

    ctx.drawImage(img1, 0, 0);
    var imgData1 = ctx.getImageData(0, 0, diffCanvas.width, diffCanvas.height);
    ctx.drawImage(img2, 0, 0);
    var imgData2 = ctx.getImageData(0, 0, diffCanvas.width, diffCanvas.height);

    var diff = ctx.createImageData(diffCanvas.width, diffCanvas.height);
    pixelmatch(imgData1.data, imgData2.data, diff.data, diffCanvas.width, diffCanvas.height, {threshold: thresholdValue});
    ctx.putImageData(diff, 0, 0);
}

