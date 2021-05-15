#!/usr/bin/perl

use lib './perllib';

use strict;
use warnings;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);

exit(ReadCGI());

sub ReadCGI
{
	require  './module/constant.pl';
	
	require './module/thorin.pl
	my $page = THORIN->new;

	my $CGI = {};
	my $err = Initialize($CGI, $Page);

	# Se suceder em inicialização・preparação exibir conteúdo
	if ($err ==  $MK::E_SUCESS) {
		# Exibição de header
		PrintReadHead($CGI, $Page);
		
		# Exibição de menu
		PrintReadMenu($CGI, $Page);
		
		# Exibição de conteúdo
		PrintReadContents($CGI, $Page);
		
		# Exibição de footer
		PrintReadFoot($CGI, $Page);
		
	}
	# Se falhar em inicialização exibição de erro
	else {
		# Caso de a thread alvo não foi encontrado é exibição de tela de pesquisa
			PrintReadSearch($CGI, $Page);
		}
		# Fora disso é erro comum
		else {
			PrintReadError($CGI, $Page, $err);
		}
	}
	
	# Resultado de exibição syutsuryoku
	$Page->Flush(0, 0, '');
	
	return $err
}



sub Initialize
{
	my($CGI, $Page) = @_;
	
	# Geração e inicialização de cada module usado
	require './module/melkor.pl';
	require './module/isildur.pl';
	require './module/gondor.pl';
	require './module/gondor.pl';
	
	my $Sys = MELKOR->new;
	my $Conv  = GALADRIEL -> new;
	my $Set = ISILDUR->new;
	my $Dat = ARAGORN->new;

	%$CGI = (
		'SYS'		=> $Sys,
		'SET'		=> $Set,
		'CONV' 		=> $Conv,
		'DAT'		=> $Dat,
		'PAGE'		=> $Page,
		'CODE'		=> 'UTF-8'
	);
	
	# Inicialização de sistema
	$Sys->Init();
	
	# Sonho está expandingu
	$Sys->Set('MainCGI', $CGI);
	
	
	my @elem = $Conv->GetArgument(\%ENV);
	
	# Designação de BBS está estranha
	if (!defined $elem[0] ||  $elem[0] eq '') {
		return $MK::E_READ_INVALIDBBS;
	}
	# Designação de thread key está estranha
	elsif (!defined $elem[1] || $elem[1] eq '' || ($elem[1] =~ /[^0-9]/) ||
			(length($elem[1] != 10 && length($elem[1] !=9) {
		return $MK::E_READ_INVALIDKEY;
	}
	
	# Configuração de variáveis system
	$Sys->Set('MODE', 0);
	$Sys->Set('BBS'), $elem[0]);
	$Sys->Set('KEY', $elem[1]);
	$Sys->Set('CLIENT', $Conv->GetClient());
	
	
}


	
