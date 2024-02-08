#!/usr/bin/perl
#============================================================================================================
#
#	Lerdasi専用CGI
#
#============================================================================================================

use lib './perllib';

use strict;
#use warnings;
no warnings 'once';
##use CGI::Carp qw(fatalsToBrowser warningsToBrowser);


# Usar resultado de execução CGI como fim code
exit(ReadCGI());

#------------------------------------------------------------------------------------------------------------
#
#	read.cgi main
#	-------------------------------------------------------------------------------------
#	@param	sem
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub ReadCGI
{
	require './module/constant.pl';

	require './module/thorin.pl';
	my $Page = THORIN->new;

	my $CGI = {};
	my $err = Initialize($CGI, $Page);

	# Inicialização・Se obter sucesso em preparação conteúdo exibição
	if ($err == $ZP::E_SUCCESS) {
		# Header exibição
		PrintReadHead($CGI, $Page);

		# Menu exibição
		PrintReadMenu($CGI, $Page);

		# Conteúdo exibição
		PrintReadContents($CGI, $Page);

		# Footer exibição
		PrintReadFoot($CGI, $Page);
	}
	# Se falhar na inicialização error exibição
	else {
		# Caso de a thread alvo não ser encontrada é exibir tela de busca
		if ($err == $ZP::E_PAGE_FINDTHREAD) {
			PrintReadSearch($CGI, $Page);
		}
		# Fora disso é erro comum
		else {
			PrintReadError($CGI, $Page, $err);
		}
	}

	# Sair resultados de exibição
	$Page->Flush(0, 0, '');

	return $err;
}

#------------------------------------------------------------------------------------------------------------
#
#	read.cgi inicialização・antes preparação
#	-------------------------------------------------------------------------------------
#	@param	$CGI
#	@param	$Page
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub Initialize
{
	my ($CGI, $Page) = @_;

	# Geração e inicialização de cada module em uso
	require './module/melkor.pl';
	require './module/isildur.pl';
	require './module/gondor.pl';
	require './module/galadriel.pl';

	my $Sys = MELKOR->new;
	my $Conv = GALADRIEL->new;
	my $Set = ISILDUR->new;
	my $Dat = ARAGORN->new;

	%$CGI = (
		'SYS'		=> $Sys,
		'SET'		=> $Set,
		'CONV'		=> $Conv,
		'DAT'		=> $Dat,
		'PAGE'		=> $Page,
		'CODE'		=> 'UTF-8',
	);

	# system inicialização
	$Sys->Init();

	# sonho está expandingu
	$Sys->Set('MainCGI', $CGI);

	# Análise de começo de operação parâmetros
	my @elem = $Conv->GetArgument(\%ENV);

	# BBS apontamento é estranho
	if (!defined $elem[0] || $elem[0] eq '') {
		return $ZP::E_READ_INVALIDBBS;
	}
	# Thread key apontamento é estranho
	elsif (!defined $elem[1] || $elem[1] eq '' || ($elem[1] =~ /[^0-9]/) ||
			(length($elem[1]) != 10 && length($elem[1]) != 9)) {
		return $ZP::E_READ_INVALIDKEY;
	}

	# System variável configuração
	$Sys->Set('MODE', 0);
	$Sys->Set('BBS', $elem[0]);
	$Sys->Set('KEY', $elem[1]);
	$Sys->Set('CLIENT', $Conv->GetClient());
	$Sys->Set('AGENT', $Conv->GetAgentMode($Sys->Get('CLIENT')));
	$Sys->Set('BBSPATH_ABS', $Conv->MakePath($Sys->Get('CGIPATH'), $Sys->Get('BBSPATH')));
	$Sys->Set('BBS_ABS', $Conv->MakePath($Sys->Get('BBSPATH_ABS'), $Sys->Get('BBS')));
	$Sys->Set('BBS_REL', $Conv->MakePath($Sys->Get('BBSPATH'), $Sys->Get('BBS')));

	# Falha na leitura de arquivo de configuração
	if ($Set->Load($Sys) == 0) {
		return $ZP::E_READ_FAILEDLOADSET;
	}

	my $submax = $Set->Get('BBS_SUBJECT_MAX') || $Sys->Get('SUBMAX');
	$Sys->Set('SUBMAX', $submax);
	my $resmax = $Set->Get('BBS_RES_MAX') || $Sys->Get('RESMAX');
	$Sys->Set('RESMAX', $resmax);

	my $path = $Conv->MakePath($Sys->Get('BBSPATH')."/$elem[0]/dat/$elem[1].dat");

	# Falha na leitura de dat file
	if ($Dat->Load($Sys, $path, 1) == 0) {
		return $ZP::E_READ_FAILEDLOADDAT;
	}
	$Dat->Close();

	# Configuração de exibição começo fim posição
	my @regs = $Conv->RegularDispNum(
				$Sys, $Dat, $elem[2], $elem[3], $elem[4]);
	$Sys->SetOption($elem[2], $regs[0], $regs[1], $elem[5], $elem[6]);

	return $ZP::E_SUCCESS;
}

#------------------------------------------------------------------------------------------------------------
#
#	read.cgi header saída
#	-------------------------------------------------------------------------------------
#	@param	$CGI
#	@param	$Page
#	@param	$title
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintReadHead
{
	my ($CGI, $Page, $title) = @_;

	my $Sys = $CGI->{'SYS'};
	my $Set = $CGI->{'SET'};
	my $Dat = $CGI->{'DAT'};

	require './module/legolas.pl';
	require './module/denethor.pl';
	my $Caption = LEGOLAS->new;
	my $Banner = DENETHOR->new;

	$Caption->Load($Sys, 'META');
	$Banner->Load($Sys);

	my $code = $CGI->{'CODE'};
	$title = $Dat->GetSubject() if(!defined $title);
	$title = '' if(!defined $title);

	# HTML saída de header
	$Page->Print("Content-type: text/html\n\n");
	$Page->Print(<<HTML);
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html lang="ja">
<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8">

 
 <meta http-equiv="Content-Style-Type" content="text/css">
 <meta name="viewport" content="width=device-width, initial-scale=1">
HTML

	$Caption->Print($Page, undef);

	$Page->Print(" <title>$title</title>\n\n");
	$Page->Print("</head>\n<!--nobanner-->\n");

	# <body> tag saída
	{
		my @work;
		$work[0] = $Set->Get('BBS_THREAD_COLOR');
		$work[1] = $Set->Get('BBS_TEXT_COLOR');
		$work[2] = $Set->Get('BBS_LINK_COLOR');
		$work[3] = $Set->Get('BBS_ALINK_COLOR');
		$work[4] = $Set->Get('BBS_VLINK_COLOR');

		$Page->Print("<body bgcolor=\"$work[0]\" text=\"$work[1]\" link=\"$work[2]\" ");
		$Page->Print("alink=\"$work[3]\" vlink=\"$work[4]\">\n\n");
	}

	# banner saída
	$Banner->Print($Page, 100, 2, 0) if ($Sys->Get('BANNER') & 5);
}

#------------------------------------------------------------------------------------------------------------
#
#	read.cgi menu saída
#	-------------------------------------------------------------------------------------
#	@param	$CGI
#	@param	$Page
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintReadMenu
{
	my ($CGI, $Page) = @_;

	# Antes preparação
	my $Sys = $CGI->{'SYS'};
	my $Set = $CGI->{'SET'};
	my $Dat = $CGI->{'DAT'};
	my $Conv = $CGI->{'CONV'};

	my $bbs = $Sys->Get('BBS');
	my $key = $Sys->Get('KEY');
	my $baseBBS = $Sys->Get('BBS_ABS');
	my $baseCGI = $Sys->Get('SERVER') . $Sys->Get('CGIPATH');
	my $account = $Sys->Get('COUNTER');
	my $PRtext = $Sys->Get('PRTEXT');
	my $PRlink = $Sys->Get('PRLINK');
	my $pathBBS = $baseBBS;
	my $pathAll = $Conv->CreatePath($Sys, 0, $bbs, $key, '');
	my $pathLast = $Conv->CreatePath($Sys, 0, $bbs, $key, 'l50');
	my $resNum = $Dat->Size();

	$Page->Print("<div style=\"margin:0px;\">\n");

	# Counter exibição
	#if ($account ne '') {
	#	$Page->Print('<a href="http://ofuda.cc/"><img width="400" height="15" border="0" src="http://e.ofuda.cc/');
	#	$Page->Print("disp/$account/00813400.gif\" alt=\"無料アクセスカウンターofuda.cc「全世界カウント計画」\"></a>\n");
	#}

	$Page->Print("<div style=\"margin-top:1em;\">\n");
	$Page->Print(" <span style=\"float:left;\">\n");
	$Page->Print(" <a href=\"$pathBBS/\">■Voltar ao keijiban■</a>\n");
	$Page->Print(" <a href=\"$pathAll\">Tudo</a>\n");

	# Exibição de thread menu
	for my $i (0 .. 9) {
		last if ($resNum <= $i * 100);

		my $st = $i * 100 + 1;
		my $ed = ($i + 1) * 100;
		my $pathMenu = $Conv->CreatePath($Sys, 0, $bbs, $key, "$st-$ed");
		$Page->Print(" <a href=\"$pathMenu\">$st-</a>\n");
	}
	$Page->Print(" <a href=\"$pathLast\">Mais novo 50</a>\n");
	$Page->Print(" </span>\n");
	$Page->Print(" <span style=\"float:right;\">\n");
	if ($PRtext ne '') {
		$Page->Print(" [PR]<a href=\"$PRlink\" target=\"_blank\">$PRtext</a>[PR]\n");
	}
	else {
		$Page->Print(" &nbsp;\n");
	}
	$Page->Print(" </span>&nbsp;\n");
	$Page->Print("</div>\n");
	$Page->Print("</div>\n\n");

	# Número de resu limite aviso exibição
	{
		my $rmax = $Sys->Get('RESMAX');

		if ($resNum >= $rmax) {
			$Page->Print("<div style=\"background-color:red;color:white;line-height:3em;margin:1px;padding:1px;\">\n");
			$Page->Print("Número de resu ultrapassou $rmax. Mais que isto escrita não pode.\n");
			$Page->Print("</div>\n\n");
		}
		elsif ($resNum >= $rmax - int($rmax / 20)) {
			$Page->Print("<div style=\"background-color:red;color:white;margin:1px;padding:1px;\">\n");
			$Page->Print("Número de resu ultrapassou ".($rmax-int($rmax/20)).". Quando ultrapassar $rmax se tornará incapaz de escrita.\n");
			$Page->Print("</div>\n\n");
		}
		elsif ($resNum >= $rmax - int($rmax / 10)) {
			$Page->Print("<div style=\"background-color:yellow;margin:1px;padding:1px;\">\n");
			$Page->Print("Número de resu ultrapassou ".($rmax-int($rmax/10)).". Quando ultrapassar $rmax se tornará incapaz de escrita.\n");
			$Page->Print("</div>\n\n");
		}
	}

	# thread title exibição
	{
		my $title = $Dat->GetSubject();
		my $ttlCol = $Set->Get('BBS_SUBJECT_COLOR');
		$Page->Print("<hr style=\"background-color:#888;color:#888;border-width:0;height:1px;position:relative;top:-.4em;\">\n\n");
		$Page->Print("<h1 style=\"color:$ttlCol;font-size:larger;font-weight:normal;margin:-.5em 0 0;\">$title</h1>\n\n");
		$Page->Print("<dl class=\"thread\">\n");
	}
}

#------------------------------------------------------------------------------------------------------------
#
#	read.cgi conteúdo saída
#	-------------------------------------------------------------------------------------
#	@param	$CGI
#	@param	$Page
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintReadContents
{
	my ($CGI, $Page) = @_;

	my $Sys = $CGI->{'SYS'};

	# Extensão load
	require './module/athelas.pl';
	my $Plugin = ATHELAS->new;
	$Plugin->Load($Sys);

	# Extensões válidas lista aquisição
	my @pluginSet = ();
	$Plugin->GetKeySet('VALID', 1, \@pluginSet);

	my $count = 0;
	my @commands = ();
	foreach my $id (@pluginSet) {
		# No caso de type é read.cgi é faça load e execute
		if ($Plugin->Get('TYPE', $id) & 4) {
			my $file = $Plugin->Get('FILE', $id);
			my $className = $Plugin->Get('CLASS', $id);

			if (-e "./plugin/$file") {
				require "./plugin/$file";
				my $Config = PLUGINCONF->new($Plugin, $id);
				$commands[$count] = $className->new($Config);
				$count++;
			}
		}
	}

	my $work = $Sys->Get('OPTION');
	my @elem = split(/\,/, $work);

	# 1 exibição flag está TRUE começo está 1 não é então exibir 1
	if ($elem[3] == 0 && $elem[1] != 1) {
		PrintResponse($CGI, $Page, \@commands, 1);
	}
	# Exibir resu restantes 
	for my $i ($elem[1] .. $elem[2]) {
		PrintResponse($CGI, $Page, \@commands, $i);
	}
}

#------------------------------------------------------------------------------------------------------------
#
#	read.cgi footer saída
#	-------------------------------------------------------------------------------------
#	@param	$CGI
#	@param	$Page
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintReadFoot
{
	my ($CGI, $Page) = @_;

	# Antes preparação
	my $Sys = $CGI->{'SYS'};
	my $Set = $CGI->{'SET'};
	my $Conv = $CGI->{'CONV'};
	my $Dat = $CGI->{'DAT'};

	my $bbs = $Sys->Get('BBS');
	my $key = $Sys->Get('KEY');
	my $ver = $Sys->Get('VERSION');
	my $rmax = $Sys->Get('RESMAX');
	my $datPath = $Conv->MakePath($Sys->Get('BBS_REL')."/dat/$key.dat");
	my $datSize = int((stat $datPath)[7] / 1024);
	my $cgipath = $Sys->Get('CGIPATH');

	# tamanho de dat file exibição
	$Page->Print("</dl>\n\n<font color=\"red\" face=\"Arial\"><b>${datSize}KB</b></font>\n\n");

	# Caso de ter restrição de tempo é explicação exibição
	if ($Sys->Get('LIMTIME')) {
		$Page->Print('　(Entre 08:00PM - 02:00AM de uma vez só não pode ler tudo)');
	}
	$Page->Print("<hr>\n");

	# Exibição de footer menu
	{
		# Ítem de Menu link configuração
		my @elem = split(/\,/, $Sys->Get('OPTION'));
		my $nxt = ($elem[2] + 100 > $rmax ? $rmax : $elem[2] + 100);
		my $nxs = $elem[2];
		my $prv = ($elem[1] - 100 < 1 ? 1 : $elem[1] - 100);
		my $prs = $prv + 100;

		# Exibição de nova chegada
		if ($rmax > $Dat->Size()) {
			my $dispStr = ($Dat->Size() == $elem[2] ? 'Exibição de nova chegada' : 'Ler a continuação');
			my $pathNew = $Conv->CreatePath($Sys, 0, $bbs, $key, "$elem[2]-");
			$Page->Print("<center><a href=\"$pathNew\">$dispStr</a></center>\n");
			$Page->Print("<hr>\n\n");
		}

		# Configuração de path
		my $pathBBS = $Sys->Get('BBS_ABS');
		my $pathAll = $Conv->CreatePath($Sys, 0, $bbs, $key, '');
		my $pathPrev = $Conv->CreatePath($Sys, 0, $bbs, $key, "$prv-$prs");
		my $pathNext = $Conv->CreatePath($Sys, 0, $bbs, $key, "$nxs-$nxt");
		my $pathLast = $Conv->CreatePath($Sys, 0, $bbs, $key, 'l50');

		$Page->Print("<div class=\"links\">\n");
		$Page->Print("<a href=\"$pathBBS/\">Voltar ao keijiban</a>\n");
		$Page->Print("<a href=\"$pathAll\">Tudo</a>\n");
		$Page->Print("<a href=\"$pathPrev\">Antes 100</a>\n");
		$Page->Print("<a href=\"$pathNext\">Próximo 100</a>\n");
		$Page->Print("<a href=\"$pathLast\">Mais novo 50</a>\n");
		$Page->Print("</div>\n");
	}

	# Exibição de contribuição form
	# Caso de resu ultrapassar número máximo é não exibir form
	if ($rmax > $Dat->Size()) {
		my $cookName = '';
		my $cookMail = '';
		my $tm = int(time);

		# cookie configuração ON tempo é adquirir cookie
		if (($Sys->Get('CLIENT') & $ZP::C_PC) && $Set->Equal('SUBBBS_CGI_ON', 1)) {
			require './module/radagast.pl';
			my $Cookie = RADAGAST->new;
			$Cookie->Init();
			my $sanitize = sub {
				$_ = shift;
				s/&/&amp;/g;
				s/</&lt;/g;
				s/>/&gt;/g;
				s/"/&#34;/g;
				return $_;
			};
			$cookName = &$sanitize($Cookie->Get('NAME', '', 'utf8'));
			$cookMail = &$sanitize($Cookie->Get('MAIL', '', 'utf8'));
		}

		$Page->Print(<<HTML);
<form method="POST" action="$cgipath/bbs.cgi?guid=ON">
<input type="hidden" name="bbs" value="$bbs"><input type="hidden" name="key" value="$key"><input type="hidden" name="time" value="$tm">
<input type="submit" value="Escrever">
Nome：<input type="text" name="FROM" value="$cookName" size="19">
E-mail<font size="1">（opcional）</font>：<input type="text" name="mail" value="$cookMail" size="19"><br>
<textarea rows="5" cols="70" name="MESSAGE"></textarea>
</form>
HTML
	}

	$Page->Print(<<HTML);
<div style="margin-top:4em;">
<a href="http://2-ch.heliohost.org/">2-channel</a> Ver. $ver
</div>

</body>
</html>
HTML
}

#------------------------------------------------------------------------------------------------------------
#
#	read.cgi resu exibição
#	-------------------------------------------------------------------------------------
#	@param	$CGI
#	@param	$Page
#	@param	$commands
#	@param	$n
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintResponse
{
	my ($CGI, $Page, $commands, $n) = @_;

	# Antes preparação
	my $Sys = $CGI->{'SYS'};
	my $Set = $CGI->{'SET'};
	my $Conv = $CGI->{'CONV'};
	my $Dat = $CGI->{'DAT'};

	my $pDat = $Dat->Get($n - 1);
	my @elem = split(/<>/, $$pDat);
	my $nameCol	= $Set->Get('BBS_NAME_COLOR');

	# URL e pontos citados adaptação
	$Conv->ConvertURL($Sys, $Set, 0, \$elem[3]);
	$Conv->ConvertQuotation($Sys, \$elem[3], 0);

	# Executar extensões
	$Sys->Set('_DAT_', \@elem);
	$Sys->Set('_NUM_', $n);
	foreach my $command (@$commands) {
		$command->execute($Sys, undef, 4);
	}

	$Page->Print(" <dt>$n ：");

	# mail coluna com
	if ($elem[1] eq '') {
		$Page->Print("<font color=\"$nameCol\"><b>$elem[0]</b></font>");
	}
	# mail coluna sem
	else {
		$Page->Print("<a href=\"mailto:$elem[1]\"><b>$elem[0]</b></a>");
	}
	$Page->Print("：$elem[2]</dt>\n");
	$Page->Print("  <dd>$elem[3]<br><br></dd>\n");
}

#------------------------------------------------------------------------------------------------------------
#
#	read.cgi tela de busca exibição
#	-------------------------------------------------------------------------------------
#	@param	$CGI
#	@param	$Page
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintReadSearch
{
	my ($CGI, $Page) = @_;

	return if (PrintDiscovery($CGI, $Page));

	my $Sys = $CGI->{'SYS'};
	my $Set = $CGI->{'SET'};
	my $Conv = $CGI->{'CONV'};
	my $Dat = $CGI->{'DAT'};

	my $nameCol = $Set->Get('BBS_NAME_COLOR');
	my $var = $Sys->Get('VERSION');
	my $cgipath = $Sys->Get('CGIPATH');
	my $bbs = $Sys->Get('BBS_ABS') . '/';
	my $server = $Sys->Get('SERVER');

	# Leitura de error用dat
	$Dat->Load($Sys, $Conv->MakePath('.'.$Sys->Get('DATA').'/2000000000.dat'), 1);
	my $size = $Dat->Size();

	# Não existe portanto retorna 404.
	$Page->Print("Status: 404 Not Found\n");

	PrintReadHead($CGI, $Page);

	$Page->Print("\n<div style=\"margin-top:1em;\">\n");
	$Page->Print(" <a href=\"$bbs\">■Voltar ao keijiban■</a>\n");
	$Page->Print("</div>\n");

	$Page->Print("<hr style=\"background-color:#888;color:#888;border-width:0;height:1px;position:relative;top:-.4em;\">\n\n");
	$Page->Print("<h1 style=\"color:red;font-size:larger;font-weight:normal;margin:-.5em 0 0;\">Thread apontada não existe</h1>\n\n");

	$Page->Print("\n<dl class=\"thread\">\n");

	for my $i (0 .. $size - 1) {
		my $pDat = $Dat->Get($i);
		my @elem = split(/<>/, $$pDat);
		$Page->Print(' <dt>' . ($i + 1) . ' ：');

		# mail coluna com
		if ($elem[1] eq '') {
			$Page->Print("<font color=\"$nameCol\"><b>$elem[0]</b></font>");
		}
		# mail coluna sem
		else {
			$Page->Print("<a href=\"mailto:$elem[1]\"><b>$elem[0]</b></a>");
		}
		$Page->Print("：$elem[2]</dt>\n  <dd>$elem[3]<br><br></dd>\n");
	}
	$Page->Print("</dl>\n\n");

	$Dat->Close();

	$Page->Print("<hr>\n\n");

	$Page->Print(<<HTML);
<div style="margin-top:4em;">
READ.CGI - $var<br>
<a href="http://2-ch.heliohost.org">2-channel</a>
</div>

</body>
</html>
HTML

}

#------------------------------------------------------------------------------------------------------------
#
#	read.cgi error exibição
#	-------------------------------------------------------------------------------------
#	@param	$CGI
#	@param	$Page
#	@param	$err
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintReadError
{
	my ($CGI, $Page, $err) = @_;

	my $code = $CGI->{'CODE'};

	# HTML header saída
	$Page->Print("Content-type: text/html\n\n");
	$Page->Print('<html><head><title>ＥＲＲＯＲ！！</title>');
	$Page->Print("");
	$Page->Print('</head><!--nobanner-->');
	$Page->Print('<html><body>');
	$Page->Print("<b>$err</b>");
	$Page->Print('</body></html>');
}

#------------------------------------------------------------------------------------------------------------
#
#	read.cgi kako log armazém busca
#	--------------------------------------------------------------------------------------
#	@param	$CGI
#	@param	$Page
#	@return	log e não encontrar em qualquer lugar retornar 0
#			se tem log retornar 1
#
#------------------------------------------------------------------------------------------------------------
sub PrintDiscovery
{
	my ($CGI, $Page) = @_;

	my $Sys = $CGI->{'SYS'};
	my $Conv = $CGI->{'CONV'};

	my $cgipath = $Sys->Get('CGIPATH');
	my $spath = $Sys->Get('BBS_REL');
	my $lpath = $Sys->Get('BBS_ABS');
	my $key = $Sys->Get('KEY');
	my $kh = substr($key, 0, 4) . '/' . substr($key, 0, 5);
	my $ver = $Sys->Get('VERSION');
	my $server = $Sys->Get('SERVER');

	# Há no kako log
	if (-e $Conv->MakePath("$spath/kako/$kh/$key.html")) {
		my $path = $Conv->MakePath("$lpath/kako/$kh/$key");

		my $title = "Capitão！No kako log armazém";
		PrintReadHead($CGI, $Page, $title);
		$Page->Print("\n<div style=\"margin-top:1em;\">\n");
		$Page->Print(" <a href=\"$lpath/\">■Voltar ao keijiban■</a>\n");
		$Page->Print("</div>\n\n");
		$Page->Print("<hr style=\"background-color:#888;color:#888;border-width:0;height:1px;position:relative;top:-.4em;\">\n\n");
		$Page->Print("<h1 style=\"color:red;font-size:larger;font-weight:normal;margin:-.5em 0 0;\">$title</h1>\n\n");
		$Page->Print("\n<blockquote>\n");
		$Page->Print("Capitão! No kako log armazém、thread <a href=\"$path.html\">$server$path.html</a>");
		$Page->Print(" <a href=\"$path.dat\">.dat</a> foi encontrada.");
		$Page->Print("</blockquote>\n");

	}
	# Há na pool
	elsif (-e $Conv->MakePath("$spath/pool/$key.cgi")) {
		my $title = "html化 esperadesu…";
		PrintReadHead($CGI, $Page, $title);
		$Page->Print("\n<div style=\"margin-top:1em;\">\n");
		$Page->Print(" <a href=\"$lpath/\">■Voltar ao keijiban■</a>\n");
		$Page->Print("</div>\n\n");
		$Page->Print("<hr style=\"background-color:#888;color:#888;border-width:0;height:1px;position:relative;top:-.4em;\">\n\n");
		$Page->Print("<h1 style=\"color:red;font-size:larger;font-weight:normal;margin:-.5em 0 0;\">$title</h1>\n\n");
		$Page->Print("\n<blockquote>\n");
		$Page->Print("$key.dat está esperando html化。");
		$Page->Print('Aqui é esperarsikanai・・・。<br>'."\n");
		$Page->Print("</blockquote>\n");
	}
	# Onde também nai
	else {
		return 0;
	}

	$Page->Print(<<HTML);

<hr>

<div style="margin-top:4em;">
READ.CGI - $ver<br>
<a href="http://2-ch.heliohost.org/">mokoichannel</a>
</div>

</body>
</html>
HTML

	return 1;
}
