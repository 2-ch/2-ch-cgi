var postflag = false;

//----------------------------------------------------------------------------------------
//	submit processamento
//----------------------------------------------------------------------------------------
function DoSubmit(modName, mode, subMode)
{
	// Configuração de informação adicional
	document.ADMIN.MODULE.value		= modName;				// モジュール名
	document.ADMIN.MODE.value		= mode;					// メインモード
	document.ADMIN.MODE_SUB.value	= subMode;				// サブモード
	
	postflag = true;
	
	// POST envio
	document.ADMIN.submit();
}

//----------------------------------------------------------------------------------------
//	opção configuração
//----------------------------------------------------------------------------------------
function SetOption(key, val)
{
	document.ADMIN.elements[key].value = val;
}

function Submitted()
{
	return postflag;
}

function toggleAll(key)
{
	var elems = document.ADMIN.elements[key];
	if (elems.length == undefined) {
		elems.checked = !elems.checked;
	} else {
		var isall = true;
		for (var i = 0; i < elems.length; i++) {
			isall = isall && elems[i].checked;
		}
		for (var i = 0; i < elems.length; i++) {
			elems[i].checked = !isall;
		}
	}
}
