var calcString = ""

$('#calc_main').dialog({
	autoOpen: false, 
	width: 215,
	resizable: false,
});

function calcButton(button)
{
	if (button == "C")
	{
		$('#calc_input').val("");
	}
	else if ( button == "=" )
	{
		// hahaha best command ever.
		$('#calc_input').val(eval($('#calc_input').val()));
	} else {
		$('#calc_input').val($('#calc_input').val() + button);
	}
}

$('#calc_btn1').button({ width: 32, height: 32 });
$('#calc_btn1').click( function () { calcButton("1"); } );
$('#calc_btn2').button({ width: 32, height: 32 });
$('#calc_btn2').click( function () { calcButton("2"); } );
$('#calc_btn3').button({ width: 32, height: 32 });
$('#calc_btn3').click( function () { calcButton("3"); } );
$('#calc_btn4').button({ width: 32, height: 32 });
$('#calc_btn4').click( function () { calcButton("4"); } );
$('#calc_btn5').button({ width: 32, height: 32 });
$('#calc_btn5').click( function () { calcButton("5"); } );
$('#calc_btn6').button({ width: 32, height: 32 });
$('#calc_btn6').click( function () { calcButton("6"); } );
$('#calc_btn7').button({ width: 32, height: 32 });
$('#calc_btn7').click( function () { calcButton("7"); } );
$('#calc_btn8').button({ width: 32, height: 32 });
$('#calc_btn8').click( function () { calcButton("8"); } );
$('#calc_btn9').button({ width: 32, height: 32 });
$('#calc_btn9').click( function () { calcButton("9"); } );
$('#calc_btn0').button({ width: 32, height: 32 });
$('#calc_btn0').click( function () { calcButton("0"); } );

$('#calc_btnplus').button({ width: 32, height: 32 });
$('#calc_btnplus').click( function () { calcButton("+"); } );
$('#calc_btnminus').button({ width: 32, height: 32 });
$('#calc_btnminus').click( function () { calcButton("-"); } );
$('#calc_btnmultiply').button({ width: 32, height: 32 });
$('#calc_btnmultiply').click( function () { calcButton("*"); } );
$('#calc_btndivide').button({ width: 32, height: 32 });
$('#calc_btndivide').click( function () { calcButton("/"); } );
$('#calc_btnclr').button({ width: 32, height: 32 });
$('#calc_btnclr').click( function () { calcButton("C"); } );
$('#calc_btnequals').button({ width: 32, height: 32 });
$('#calc_btnequals').click( function () { calcButton("="); } );
