#!/usr/bin/perl
#============================================================================================================
#
#	Escrita用CGI
#
#============================================================================================================

use lib './perllib';

use strict;
#use warnings;
no warnings 'once';
##use CGI::Carp qw(fatalsToBrowser warningsToBrowser);


# Usar resultado de execução CGI como fim code
exit(BBSCGI());

#------------------------------------------------------------------------------------------------------------
#
#	bbs.cgi main
#	-------------------------------------------------------------------------------------
#	@param	sem
#	@return	número de erro
#
#------------------------------------------------------------------------------------------------------------
sub BBSCGI
{
	require './module/constant.pl';

	require './module/thorin.pl';
	my $Page = THORIN->new;

	my $CGI = {};
	my $err = $ZP::E_SUCCESS;

	$err = Initialize($CGI, $Page);
	# Se tiver sucesso na inicialização começar processo de escrita
	if ($err == $ZP::E_SUCCESS) {
		my $Sys = $CGI->{'SYS'};
		my $Form = $CGI->{'FORM'};
		my $Set = $CGI->{'SET'};
		my $Conv = $CGI->{'CONV'};
		my $Threads = $CGI->{'THREADS'};

		require './module/vara.pl';
		my $WriteAid = VARA->new;
		$WriteAid->Init($Sys, $Form, $Set, $Threads, $Conv);

		$err = $WriteAid->Write();
		# Se tiver sucesso na escrita atualizar keijiban estrutura elemento
		if ($err == $ZP::E_SUCCESS) {
			if (!$Sys->Equal('FASTMODE', 1)) {
				require './module/varda.pl';
				my $BBSAid = VARDA->new;

				$BBSAid->Init($Sys, $Set);
				$BBSAid->CreateIndex();
				$BBSAid->CreateIIndex();
				$BBSAid->CreateSubback();
			}
			PrintBBSJump($CGI, $Page);
		}
		else {
			PrintBBSError($CGI, $Page, $err);
		}
	}
	else {
		# Thread criação tela exibição
		if ($err == $ZP::E_PAGE_THREAD) {
			PrintBBSThreadCreate($CGI, $Page);
			$err = $ZP::E_SUCCESS;
		}
		# cookie verificação tela exibição
		elsif ($err == $ZP::E_PAGE_COOKIE) {
			PrintBBSCookieConfirm($CGI, $Page);
			$err = $ZP::E_SUCCESS;
		}
		# De keitai thread criação tela exibição
		elsif ($err == $ZP::E_PAGE_THREADMOBILE) {
			PrintBBSMobileThreadCreate($CGI, $Page);
			$err = $ZP::E_SUCCESS;
		}
		# Error tela exibição
		else {
			PrintBBSError($CGI, $Page, $err);
		}
	}

	# Exibição de resultado
	$Page->Flush('', 0, 0);

	return $err;
}

#------------------------------------------------------------------------------------------------------------
#
#	bbs.cgi Inicialização
#	-------------------------------------------------------------------------------------
#	@param	$CGI
#	@param	$Page
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub Initialize
{
	my ($CGI, $Page) = @_;

	# Inicialização de módulos em uso
	require './module/melkor.pl';
	require './module/isildur.pl';
	require './module/radagast.pl';
	require './module/galadriel.pl';
	require './module/samwise.pl';
	require './module/baggins.pl';

	my $Sys = MELKOR->new;
	my $Conv = GALADRIEL->new;
	my $Set = ISILDUR->new;
	my $Cookie = RADAGAST->new;
	my $Threads = BILBO->new;

	# System informação configuração
	return $ZP::E_SYSTEM_ERROR if ($Sys->Init());

	my $Form = SAMWISE->new($Sys->Get('BBSGET'));

	%$CGI = (
		'SYS'		=> $Sys,
		'SET'		=> $Set,
		'COOKIE'	=> $Cookie,
		'CONV'		=> $Conv,
		'PAGE'		=> $Page,
		'FORM'		=> $Form,
		'THREADS'	=> $Threads,
	);

	# Sonho está expandingu
	$Sys->Set('MainCGI', $CGI);

	# form informação configuração
	$Form->DecodeForm(1);

	# Host informação configuração(DNS resolução reversa)
	#Variável inicialização check inserir。
	if(!defined $ENV{'REMOTE_HOST'} || $ENV{'REMOTE_HOST'} eq '') {
		$ENV{'REMOTE_HOST'} = $Conv->GetRemoteHost();
	}
	$Form->Set('HOST', $ENV{'REMOTE_HOST'});

	my $client = $Conv->GetClient();

	$Sys->Set('ENCODE', 'Shift_JIS');
	$Sys->Set('BBS', $Form->Get('bbs', ''));
	$Sys->Set('KEY', $Form->Get('key', ''));
	$Sys->Set('CLIENT', $client);
	$Sys->Set('AGENT', $Conv->GetAgentMode($client));
	$Sys->Set('KOYUU', $ENV{'REMOTE_HOST'});
	$Sys->Set('BBSPATH_ABS', $Conv->MakePath($Sys->Get('CGIPATH'), $Sys->Get('BBSPATH')));
	$Sys->Set('BBS_ABS', $Conv->MakePath($Sys->Get('BBSPATH_ABS'), $Sys->Get('BBS')));
	$Sys->Set('BBS_REL', $Conv->MakePath($Sys->Get('BBSPATH'), $Sys->Get('BBS')));

	# No caso de keitai é definir informações do modelo
	if ($client & $ZP::C_MOBILE_IDGET) {
		my $product = $Conv->GetProductInfo($client);

		if (!defined $product) {
			return $ZP::E_POST_NOPRODUCT;
		}

		$Sys->Set('KOYUU', $product);
	}

	# Leitura de SETTING.TXT
	if (!$Set->Load($Sys)) {
		return $ZP::E_POST_NOTEXISTBBS;
	}

	# De keitai thread criação form exibição
	# $S->Equal('AGENT', 'O') &&
	if ($Form->Equal('mb', 'on') && $Form->Equal('thread', 'on')) {
		return $ZP::E_PAGE_THREADMOBILE;
	}

	my $submax = $Set->Get('BBS_SUBJECT_MAX') || $Sys->Get('SUBMAX');
	$Sys->Set('SUBMAX', $submax);
	my $resmax = $Set->Get('BBS_RES_MAX') || $Sys->Get('RESMAX');
	$Sys->Set('RESMAX', $resmax);

	# Em form informação se key existe resu escrita
	if ($Form->IsExist('key'))	{ $Sys->Set('MODE', 2); }
	else						{ $Sys->Set('MODE', 1); }

	# No thread criação mode MESSAGE não há：thread criação tela
	if ($Sys->Equal('MODE', 1)) {
		if (!$Form->IsExist('MESSAGE')) {
			return $ZP::E_PAGE_THREAD;
		}
		$Form->Set('key', int(time));
		$Sys->Set('KEY', $Form->Get('key'));
	}

	# Existência de cookie check(PC apenas)
	if ($client & $ZP::C_PC) {
		if ($Set->Equal('SUBBBS_CGI_ON', 1)) {
			# ambiente variável aquisição falha
			if (!$Cookie->Init()) {
				return $ZP::E_PAGE_COOKIE;
			}

			# Nome coluna cookie
			if ($Set->Equal('BBS_NAMECOOKIE_CHECK', 'checked') && !$Cookie->IsExist('NAME')) {
				return $ZP::E_PAGE_COOKIE;
			}
			# mail coluna cookie
			if ($Set->Equal('BBS_MAILCOOKIE_CHECK', 'checked') && !$Cookie->IsExist('MAIL')) {
				return $ZP::E_PAGE_COOKIE;
			}
		}
	}

	# Leitura de subject
	$Threads->Load($Sys);

	return $ZP::E_SUCCESS;
}

#------------------------------------------------------------------------------------------------------------
#
#	bbs.cgi thread criação page exibição
#	-------------------------------------------------------------------------------------
#	@param	$CGI
#	@param	$Page
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintBBSThreadCreate
{
	my ($CGI, $Page) = @_;

	my $Sys = $CGI->{'SYS'};
	my $Set = $CGI->{'SET'};
	my $Form = $CGI->{'FORM'};
	my $Cookie = $CGI->{'COOKIE'};

	require './module/legolas.pl';
	my $Caption = LEGOLAS->new;
	$Caption->Load($Sys, 'META');

	my $title = $Set->Get('BBS_TITLE');
	my $link = $Set->Get('BBS_TITLE_LINK');
	my $image = $Set->Get('BBS_TITLE_PICTURE');
	my $code = $Sys->Get('ENCODE');
	my $cgipath = $Sys->Get('CGIPATH');

	# HTML saída de header
	$Page->Print("Content-type: text/html\n\n");
	$Page->Print("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\" \"http://www.w3.org/TR/html4/loose.dtd\">\n");
	$Page->Print("<html lang=\"ja\">\n");
	$Page->Print("<head>\n");
	$Page->Print(' <meta http-equiv="Content-Type" content="text/html;charset=Shift_JIS">'."\n\n");
	$Caption->Print($Page, undef);
	$Page->Print(" <title>$title</title>\n\n");
	$Page->Print("</head>\n<!--nobanner-->\n");

	# <body> tag saída
	{
		my @work;
		$work[0] = $Set->Get('BBS_BG_COLOR');
		$work[1] = $Set->Get('BBS_TEXT_COLOR');
		$work[2] = $Set->Get('BBS_LINK_COLOR');
		$work[3] = $Set->Get('BBS_ALINK_COLOR');
		$work[4] = $Set->Get('BBS_VLINK_COLOR');
		$work[5] = $Set->Get('BBS_BG_PICTURE');

		$Page->Print("<body bgcolor=\"$work[0]\" text=\"$work[1]\" link=\"$work[2]\" ");
		$Page->Print("alink=\"$work[3]\" vlink=\"$work[4]\" ");
		$Page->Print("background=\"$work[5]\">\n");
	}

	$Page->Print("<div align=\"center\">");
	# Kanban imagem exibição com
	if ($image ne '') {
		# No kanban imagem tem
		if ($link ne '') {
			$Page->Print("<a href=\"$link\"><img src=\"$image\" border=\"0\" alt=\"$image\"></a><br>");
		}
		# No kanban imagem link não tem
		else {
			$Page->Print("<img src=\"$image\" border=\"0\"><br>");
		}
	}
	$Page->Print("</div>");

	# Exibição de header table
	$Caption->Load($Sys, 'HEAD');
	$Caption->Print($Page, $Set);

	# Exibição de criação de thread form
	{
		my $tblCol = $Set->Get('BBS_MAKETHREAD_COLOR');
		my $name = $Cookie->Get('NAME', '', 'utf8');
		my $mail = $Cookie->Get('MAIL', '', 'utf8');
		my $bbs = $Form->Get('bbs');
		my $tm = int(time);
		my $ver = $Sys->Get('VERSION');

		$Page->Print(<<HTML);
<table border="1" cellspacing="7" cellpadding="3" width="95%" bgcolor="$tblCol" align="center">
 <tr>
  <td>
  <b>Nova criação de thread</b><br>
  <center>
  <form method="POST" action="./bbs.cgi?guid=ON">
  <input type="hidden" name="bbs" value="$bbs"><input type="hidden" name="time" value="$tm">
  <table border="0">
   <tr>
    <td align="left">
    Title：<input type="text" name="subject" size="25">　<input type="submit" value="Criação de thread nova"><br>
    Nome：<input type="text" name="FROM" size="19" value="$name">
    E-mail<font size="1">（opcional）</font>：<input type="text" name="mail" size="19" value="$mail"><br>
    <textarea rows="5" cols="64" name="MESSAGE"></textarea>
    </td>
   </tr>
  </table>
  </form>
  </center>
  </td>
 </tr>
</table>

<p>
$ver
</p>
HTML
	}

	$Page->Print("\n</body>\n</html>\n");
}

#------------------------------------------------------------------------------------------------------------
#
#	bbs.cgi criação de thread page(keitai) exibição
#	-------------------------------------------------------------------------------------
#	@param	$CGI
#	@param	$Page	THORIN
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintBBSMobileThreadCreate
{
	my ($CGI, $Page) = @_;

	my $Sys = $CGI->{'SYS'};
	my $Set = $CGI->{'SET'};

	require './module/denethor.pl';
	my $Banner = DENETHOR->new;
	$Banner->Load($Sys);

	my $title = $Set->Get('BBS_TITLE');
	my $bbs = $Sys->Get('BBS');
	my $tm = int(time);

	$Page->Print("Content-type: text/html\n\n");
	$Page->Print("<html><head><title>$title</title></head><!--nobanner-->");
	$Page->Print("\n<body><form action=\"./bbs.cgi?guid=ON\" method=\"POST\"><center>$title<hr>");

	$Banner->Print($Page, 100, 2, 1);

	$Page->Print("</center>\n");
	$Page->Print("Title<br><input type=text name=subject><br>");
	$Page->Print("Nome<br><input type=text name=FROM><br>");
	$Page->Print("Mail<br><input type=text name=mail><br>");
	$Page->Print("<textarea name=MESSAGE></textarea><br>");
	$Page->Print("<input type=hidden name=bbs value=$bbs>");
	$Page->Print("<input type=hidden name=time value=$tm>");
	$Page->Print("<input type=hidden name=mb value=on>");
	$Page->Print("<input type=submit value=\"Criação de thread\">");
	$Page->Print("</form></body></html>");
}

#------------------------------------------------------------------------------------------------------------
#
#	bbs.cgi cookie verificação page exibição
#	-------------------------------------------------------------------------------------
#	@param	$CGI
#	@param	$Page	THORIN
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintBBSCookieConfirm
{
	my ($CGI, $Page) = @_;

	my $Sys = $CGI->{'SYS'};
	my $Form = $CGI->{'FORM'};
	my $Set = $CGI->{'SET'};
	my $Cookie = $CGI->{'COOKIE'};

	my $sanitize = sub {
		$_ = shift;
		s/&/&amp;/g;
		s/</&lt;/g;
		s/>/&gt;/g;
		s/"/&#34;/g;
		return $_;
	};
	my $code = $Sys->Get('ENCODE');
	my $bbs = &$sanitize($Form->Get('bbs'));
	my $tm = int(time);
	my $name = &$sanitize($Form->Get('FROM'));
	my $mail = &$sanitize($Form->Get('mail'));
	my $msg = &$sanitize($Form->Get('MESSAGE'));
	my $subject = &$sanitize($Form->Get('subject'));
	my $key = &$sanitize($Form->Get('key'));

	# cookie saída de informação
	$Cookie->Set('NAME', $name, 'utf8')	if ($Set->Equal('BBS_NAMECOOKIE_CHECK', 'checked'));
	$Cookie->Set('MAIL', $mail, 'utf8')	if ($Set->Equal('BBS_MAILCOOKIE_CHECK', 'checked'));
	$Cookie->Out($Page, $Set->Get('BBS_COOKIEPATH'), 60 * 24 * 30);

	$Page->Print("Content-type: text/html\n\n");
	$Page->Print(<<HTML);
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<!-- 2ch_X:cookie -->
<head>

 <meta http-equiv="Content-Type" content="text/html; charset=Shift_JIS">

 <title>■ Verificação de escrita ■</title>

</head>
<!--nobanner-->
HTML

	# <body> tag saída
	{
		my @work;
		$work[0] = $Set->Get('BBS_THREAD_COLOR');
		$work[1] = $Set->Get('BBS_TEXT_COLOR');
		$work[2] = $Set->Get('BBS_LINK_COLOR');
		$work[3] = $Set->Get('BBS_ALINK_COLOR');
		$work[4] = $Set->Get('BBS_VLINK_COLOR');

		$Page->Print("<body bgcolor=\"$work[0]\" text=\"$work[1]\" link=\"$work[2]\" ");
		$Page->Print("alink=\"$work[3]\" vlink=\"$work[4]\">\n");
	}

	$Page->Print(<<HTML);
<font size="4" color="#FF0000"><b>Escrita＆Cookie verificação</b></font>
<blockquote style="margin-top:4em;">
 Nome： $name<br>
 E-mail： $mail<br>
 Conteúdo：<br>
 $msg<br>
</blockquote>

<div style="font-weight:bold;">
Verificação de contribuição<br>
・Contribuinte é, aceita que a responsabilidade que surge com relação a contribuição volta ao contribuinte.<br>
・Contribuinte é, com relação a contribuições de anúncios sem relevância ao tema, concorda em pagar uma taxa razoável.<br>
・Contribuinte é, Sobre o conteúdo contribuido, permite que o operador do keijiban copie, salve, cite, reimprima entre outros usos.<br>
　Também, a respeito do operador do keijiban, concorda não exercer em absoluto nenhum direito moral.<br>
・Contribuinte é, a respeito dos terceiros indicados pelo operador do keijiban, concorda absolutamente não fazer licença de coisas protegidas por direitos autorais.<br>
</div>

<form method="POST" action="./bbs.cgi?guid=ON">
HTML

	$msg =~ s/<br>/\n/g;

	$Page->HTMLInput('hidden', 'subject', $subject);
	$Page->HTMLInput('hidden', 'FROM', $name);
	$Page->HTMLInput('hidden', 'mail', $mail);
	$Page->HTMLInput('hidden', 'MESSAGE', $msg);
	$Page->HTMLInput('hidden', 'bbs', $bbs);
	$Page->HTMLInput('hidden', 'time', $tm);

	# No caso de resu escrita mode é configurar key
	if ($Sys->Equal('MODE', 2)) {
		$Page->HTMLInput('hidden', 'key', $key);
	}

	$Page->Print(<<HTML);
<input type="submit" value="上記全てを承諾して書き込む"><br>
</form>

<p>
Caso de mudar é volte no botão voltar reescrevakudasai.
</p>

<p>
Atual, como arasi prevenção cookie não configurado e escrita tornará se não possível.<br>
<font size="2">(cookieを設定するとこの画面はでなくなります。)</font><br>
</p>

</body>
</html>
HTML
}


#------------------------------------------------------------------------------------------------------------
#
#	bbs.cgi jump page exibição
#	-------------------------------------------------------------------------------------
#	@param	$CGI
#	@param	$Page
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintBBSJump
{
	my ($CGI, $Page) = @_;

	my $Sys = $CGI->{'SYS'};
	my $Form = $CGI->{'FORM'};
	my $Set = $CGI->{'SET'};
	my $Conv = $CGI->{'CONV'};
	my $Cookie = $CGI->{'COOKIE'};

	# Keitai用 exibição
	if ($Form->Equal('mb', 'on') || ($Sys->Get('CLIENT') & $ZP::C_MOBILEBROWSER) ) {
		my $bbsPath = $Conv->MakePath($Sys->Get('CGIPATH').'/r.cgi/'.$Form->Get('bbs').'/'.$Form->Get('key').'/l10');
		$Page->Print("Content-type: text/html\n\n");
		$Page->Print('<!--nobanner--><html><body>Escrita conclusão desu<br>');
		$Page->Print("<a href=\"$bbsPath\">Daqui</a>");
		$Page->Print("ao keijiban voltekudasai.\n");
	}
	# PC用 exibição
	else {
		my $bbsPath = $Conv->MakePath($Sys->Get('BBS_REL'));
		my $name = $Form->Get('NAME', '');
		my $mail = $Form->Get('MAIL', '');

		$Cookie->Set('NAME', $name, 'utf8')	if ($Set->Equal('BBS_NAMECOOKIE_CHECK', 'checked'));
		$Cookie->Set('MAIL', $mail, 'utf8')	if ($Set->Equal('BBS_MAILCOOKIE_CHECK', 'checked'));
		$Cookie->Out($Page, $Set->Get('BBS_COOKIEPATH'), 60 * 24 * 30);

		$Page->Print("Content-type: text/html\n\n");
		$Page->Print(<<HTML);
<html>
<head>
	<title>Escrito.</title>
<meta http-equiv="Content-Type" content="text/html; charset=Shift_JIS">
<meta http-equiv="Refresh" content="5;URL=$bbsPath/">
</head>
<!--nobanner-->
<body>
Escrita terminou.<br>
<br>
Até a tela mudar um tempo esperekudasai.<br>
<br>
<br>
<br>
<br>
<hr>
HTML

	}
	# kokuchi coluna exibição (caso não querer exibição é commentout ou condição para 0)
	if (0) {
		require './module/denethor.pl';
		my $Banner = DENETHOR->new;
		$Banner->Load($Sys);
		$Banner->Print($Page, 100, 0, $Sys->Get('AGENT'));
	}
	$Page->Print("\n</body>\n</html>\n");
}

#------------------------------------------------------------------------------------------------------------
#
#	bbs.cgi error page exibição
#	-------------------------------------------------------------------------------------
#	@param	$CGI
#	@param	$Page
#	@param	$err
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintBBSError
{
	my ($CGI, $Page, $err) = @_;

	require './module/orald.pl';
	my $Error = ORALD->new;
	$Error->Load($CGI->{'SYS'});

	$Error->Print($CGI, $Page, $err, $CGI->{'SYS'}->Get('AGENT'));
}

