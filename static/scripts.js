$(document).ready(function() {
$('.article-show').each(function() {
$('.article-show').hide();
 
 $('.article-show > .demo-row > .span2 > button').click(function() { 
 	$.ajax({
 		type: 'POST',
 		url: "/initpref", // change this to work for ALL choice buttons
		data: {"story_id": event.currentTarget.id, "pref": event.currentTarget.value},
		success:function(response){
			console.log(response);
		},
 	});
 	$(this).parent().parent().parent().addClass('animated fadeOutRightBig');
 	$(this).parent().parent().parent().hide().next().show().addClass('animated fadeInLeftBig');
   });
 $('.article-show > .demo-row > .span2 > button').eq(0).trigger('click');
});
});




