// colors each letter of string based on corresponding hex value
function colorText(text, colors) {
    var res = '';
    for (i=0; i < text.length; i++) {
        res += "<span style='color: " + colors[i] +";'>"+ text[i] + "</span>";
    }
    return res;
}
