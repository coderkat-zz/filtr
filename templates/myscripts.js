$(document).ready(function() {
   $("a").click(function() {
     alert("Hello world!");
   });
});

$(document).ready(function() {
	$("#orderedlist").addClass("red");
});


$(document).ready(function() {
	$("#oderedlist li:last").hover(function() {
		$(this).addClass("green");
	},function() {
		$(this).removeClass("green");
	});
  });

