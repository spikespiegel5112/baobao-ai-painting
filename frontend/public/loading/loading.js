window.onload = function () {
    var loadingElement = document.createElement("div");
    var loadingHtml = [];
    loadingElement.setAttribute("id", "line-scale");
    loadingHtml.push("<div class='content'>");
    loadingHtml.push('<div></div>');
    loadingHtml.push('<div></div>');
    loadingHtml.push('<div></div>');
    loadingHtml.push('<div></div>');
    loadingHtml.push('<div></div>');
    loadingHtml.push('</div>');
    loadingHtml.push('</div>');
    loadingElement.innerHTML = loadingHtml.join("");
    document.body.appendChild(loadingElement);
    document.getElementById('line-scale');
}