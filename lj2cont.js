var post;
var lj2cont = {
    init : function() {
        $("#btn_draft").parent().parent().append("<div id='better-editor-holder'></div>");        
        $("#better-editor-holder").append("<textarea id='better-editor'></textarea>");
        $("#better-editor-holder").append("<button>Apply</button>").click(this.convertContent);
        $.getScript("http://tinymce.cachefly.net/4.2/tinymce.min.js", lj2cont.initTinyMCE);
    },
    initTinyMCE:function(){
        tinymce.init({selector:"textarea#better-editor"});
    },
    convertContent: function() {
        post = $("<div/>").append(tinyMCE.activeEditor.getContent());
        $("div *", post).unwrap();
        $("img", post).remove();

        lj2cont.replaceTag(post, "em", "i");
        lj2cont.replaceTag(post, "h4", "h4");
        lj2cont.replaceTag(post, "h3", "h3");
        lj2cont.replaceTag(post, "i", "i");
        lj2cont.replaceTag(post, "b", "b");
        lj2cont.replaceTag(post, "p", "p");
        lj2cont.replaceTag(post, "u", "u");
        lj2cont.replaceStrong(post);
        lj2cont.replaceLineBreaks(post);
        lj2cont.removeEmptyLinks(post);
        lj2cont.fixLinks(post);
        $(":not(a, i, b, p, h4, h3, blockquote)", post).each(function(){
            $(this).replaceWith($(this).contents());
        });
        
        console.debug(post.html());
        //$(".editable").html(post.html());
//        $('#result').html(post);
    },
    replaceStrong : function (post) {
        $("strong", post).each(function() {
            $(this).replaceWith("<b>" + $(this).html() + "</b>");
        });
    },
    replaceLineBreaks : function (post) {
        $("p", post).each(function(){
            $(this).replaceWith($(this).html()+"<br/>")
        });
        var paragraphs = post.html().split("<br>");
        post.empty();
        $.each(paragraphs, function (i, p) { post.append($("<p>").append(p));});
    },
    removeEmptyLinks : function(post) {
        $("a", post).each(function() {
            if ($.trim($(this).attr('href')) == '' ||
                $.trim($(this).text()) == '') { 
                $(this).remove();
            }
        });                         
    },
    fixLinks : function(post) {
        $("a", post).each(function() {
            $(this).replaceWith($("<a>").attr("href", $(this).attr('href')).append($(this).contents()));
        });                         
    },
    replaceTag : function(post, from, to) {
        $(from, post).each(function() {
            $(this).replaceWith($("<"+to+"/>").append($(this).contents()));
        });
    }
};
