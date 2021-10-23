#============================================================================================================
#
#	Kako log gerenciamento module
#
#============================================================================================================
package	CELEBORN;

use strict;
#use warnings;

#------------------------------------------------------------------------------------------------------------
#
#	Constructor
#	-------------------------------------------------------------------------------------
#	@param	sem
#	@return	module object
#
#------------------------------------------------------------------------------------------------------------
sub new
{
	my $class = shift;
	
	my $obj = {
		'KEY'		=> undef,
		'SUBJECT'	=> undef,
		'DATE'		=> undef,
		'PATH'		=> undef
	};
	bless $obj, $class;
	
	return $obj;
}

#------------------------------------------------------------------------------------------------------------
#
#	Kako log informação file leitura
#	-------------------------------------------------------------------------------------
#	@param	$Sys	MELKOR
#	@return	error número
#
#------------------------------------------------------------------------------------------------------------
sub Load
{
	my $this = shift;
	my ($Sys) = @_;
	
	$this->{'KEY'} = {};
	$this->{'SUBJECT'} = {};
	$this->{'DATE'} = {};
	$this->{'PATH'} = {};
	
	my $path = $Sys->Get('BBSPATH') . '/' . $Sys->Get('BBS') . '/kako/kako.idx';
	
	if (open(my $fh, '<', $path)) {
		flock($fh, 2);
		my @lines = <$fh>;
		close($fh);
		map { s/[\r\n]+\z// } @lines;
		
		foreach (@lines) {
			next if ($_ eq '');
			
			my @elem = split(/<>/, $_);
			if (scalar(@elem) < 5) {
				warn "invalid line in $path";
				next;
			}
			
			my $id = $elem[0];
			$this->{'KEY'}->{$id} = $elem[1];
			$this->{'SUBJECT'}->{$id} = $elem[2];
			$this->{'DATE'}->{$id} = $elem[3];
			$this->{'PATH'}->{$id} = $elem[4];
		}
		return 0;
	}
	return -1;
}

#------------------------------------------------------------------------------------------------------------
#
#	Kako log informação file escrita
#	-------------------------------------------------------------------------------------
#	@param	$Sys	MELKOR
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub Save
{
	my $this = shift;
	my ($Sys) = @_;
	
	my $path = $Sys->Get('BBSPATH') . '/' . $Sys->Get('BBS') . '/kako/kako.idx';
	
	chmod($Sys->Get('PM-DAT'), $path);
	if (open(my $fh, (-f $path ? '+<' : '>'), $path)) {
		flock($fh, 2);
		seek($fh, 0, 0);
		binmode($fh);
		
		foreach (keys %{$this->{'KEY'}}) {
			my $data = join('<>',
				$_,
				$this->{'KEY'}->{$_},
				$this->{'SUBJECT'}->{$_},
				$this->{'DATE'}->{$_},
				$this->{'PATH'}->{$_}
			);
			
			print $fh "$data\n";
		}
		
		truncate($fh, tell($fh));
		close($fh);
	}
	else {
		warn "can't save subject: $path";
	}
	chmod($Sys->Get('PM-DAT'), $path);
}

#------------------------------------------------------------------------------------------------------------
#
#	ID set aquisição
#	-------------------------------------------------------------------------------------
#	@param	$kind	busca tipo
#	@param	$name	busca word
#	@param	$pBuf	ID set armazenamento buffer
#	@return	keyset número
#
#------------------------------------------------------------------------------------------------------------
sub GetKeySet
{
	my $this = shift;
	my ($kind, $name, $pBuf) = @_;
	
	my $n = 0;
	
	if ($kind eq 'ALL') {
		foreach my $key (keys %{$this->{'KEY'}}) {
			if ($this->{'KEY'}->{$key} ne '0') {
				$n += push @$pBuf, $key;
			}
		}
	}
	else {
		foreach my $key (keys %{$this->{$kind}}) {
			if ($this->{$kind}->{$key} eq $name || $kind eq 'ALL') {
				$n += push @$pBuf, $key;
			}
		}
	}
	
	return $n;
}

#------------------------------------------------------------------------------------------------------------
#
#	Informação aquisição
#	-------------------------------------------------------------------------------------
#	@param	$kind		tipo de informação
#	@param	$key		user ID
#	@param	$default	default
#	@return	user informação
#
#------------------------------------------------------------------------------------------------------------
sub Get
{
	my $this = shift;
	my ($kind, $key, $default) = @_;
	
	my $val = $this->{$kind}->{$key};
	
	return (defined $val ? $val : (defined $default ? $default : undef));
}

#------------------------------------------------------------------------------------------------------------
#
#	Adição
#	-------------------------------------------------------------------------------------
#	@param	$key		thread key
#	@param	$subject	thread title
#	@param	$date		atualização data e hora
#	@param	$path		path
#	@return	ID
#
#------------------------------------------------------------------------------------------------------------
sub Add
{
	my $this = shift;
	my ($key, $subject, $date, $path) = @_;
	
	my $id = time;
	$id++ while (exists $this->{'KEY'}->{$id});
	
	$this->{'KEY'}->{$id} = $key;
	$this->{'SUBJECT'}->{$id} = $subject;
	$this->{'DATE'}->{$id} = $date;
	$this->{'PATH'}->{$id} = $path;
	
	return $id;
}

#------------------------------------------------------------------------------------------------------------
#
#	Informação configuração
#	-------------------------------------------------------------------------------------
#	@param	$id		ID
#	@param	$kind	informação tipo
#	@param	$val	configuração valor
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub Set
{
	my $this = shift;
	my ($id, $kind, $val) = @_;
	
	if (exists $this->{$kind}->{$id}) {
		$this->{$kind}->{$id} = $val;
	}
}

#------------------------------------------------------------------------------------------------------------
#
#	Informação apagação
#	-------------------------------------------------------------------------------------
#	@param	$id		apagação ID
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub Delete
{
	my $this = shift;
	my ($id) = @_;
	
	delete $this->{'KEY'}->{$id};
	delete $this->{'SUBJECT'}->{$id};
	delete $this->{'DATE'}->{$id};
	delete $this->{'PATH'}->{$id};
}

#------------------------------------------------------------------------------------------------------------
#
#	Kako log informação atualização
#	-------------------------------------------------------------------------------------
#	@param	$Sys	MELKOR
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub UpdateInfo
{
	my $this = shift;
	my ($Sys) = @_;
	
	require './module/earendil.pl';
	
	$this->{'KEY'} = {};
	$this->{'SUBJECT'} = {};
	$this->{'DATE'} = {};
	$this->{'PATH'} = {};
	
	my $path = $Sys->Get('BBSPATH') . '/' . $Sys->Get('BBS') . '/kako';
	
	# Obter directory informação
	my $hierarchy = {};
	my @dirList = ();
	EARENDIL::GetFolderHierarchy($path, $hierarchy);
	EARENDIL::GetFolderList($hierarchy, \@dirList, '');
	
	foreach my $dir (@dirList) {
		my @fileList = ();
		EARENDIL::GetFileList("$path/$dir", \@fileList, '([0-9]+)\.html');
		$this->Add(0, 0, 0, $dir);
		foreach my $file (sort @fileList) {
			my @elem = split(/\./, $file);
			my $subj = GetThreadSubject("$path/$dir/$file");
			if (defined $subj) {
				$this->Add($elem[0], $subj, time, $dir);
			}
		}
	}
}

#------------------------------------------------------------------------------------------------------------
#
#	Atualização de kako log index
#	-------------------------------------------------------------------------------------
#	@param	$Sys	MELKOR
#	@param	$Page	
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub UpdateIndex
{
	my $this = shift;
	my ($Sys, $Page) = @_;
	
	# kokuchi informação leitura
	require './module/denethor.pl';
	my $Banner = DENETHOR->new;
	$Banner->Load($Sys);
	
	my $basePath = $Sys->Get('BBSPATH') . '/' . $Sys->Get('BBS');
	
	# Fazer a path em key e criar hash
	my %PATHES = ();
	foreach my $id (keys %{$this->{'KEY'}}) {
		my $path = $this->{'PATH'}->{$id};
		$PATHES{$path} = $id;
	}
	my @dirs = keys %PATHES;
	unshift @dirs, '';
	
	# Para cada path criar index
	foreach my $path (@dirs) {
		my @info = ();
		
		# Obter subfolder 1 andar abaixo
		my @folderList = ();
		GetSubFolders($path, \@dirs, \@folderList);
		foreach my $dir (sort @folderList) {
			push @info, "0<>0<>0<>$dir";
		}
		
		# Se tiver log data adicionar ao informação arranjo
		foreach my $id (keys %{$this->{'KEY'}}) {
			if ($path eq $this->{'PATH'}->{$id} && $this->{'KEY'}->{$id} ne '0') {
				my $data = join('<>',
					$this->{'KEY'}->{$id},
					$this->{'SUBJECT'}->{$id},
					$this->{'DATE'}->{$id},
					$path
				);
				push @info, "$data";
			}
		}
		
		# Sair index file
		$Page->Clear();
		OutputIndex($Sys, $Page, $Banner, \@info, $basePath, $path);
		chmod($Sys->Get('PM-KDIR'), "$basePath/kako$path");
	}
}

#------------------------------------------------------------------------------------------------------------
#
#	Obter subfolder
#	-------------------------------------------------------------------------------------
#	@param	$base	Parente folder path
#	@param	$pDirs	Arranjo de directory nome
#	@param	$pList	Subfolder armazenamento arranjo
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub GetSubFolders
{
	
	my ($base, $pDirs, $pList) = @_;
	
	# Ao fazer foreach my $dir destrói $pDir
	foreach (@$pDirs) {
		my $dir = $_;
		if ($dir =~ s|^\Q$base/\E|| && $dir !~ m|/|) {
			push @$pList, $dir;
		}
	}
}

#------------------------------------------------------------------------------------------------------------
#
#	Aquisição de kako log title
#	-------------------------------------------------------------------------------------
#	@param	$path	path para file adquirir
#	@return	title
#
#------------------------------------------------------------------------------------------------------------
sub GetThreadSubject
{
	
	my ($path) = @_;
	my $title = undef;
	
	if (open(my $fh, '<', $path)) {
		flock($fh, 2);
		my @lines = <$fh>;
		close($fh);
		
		foreach (@lines) {
			if ($_ =~ m|<title>(.*)</title>|) {
				$title = $1;
				last;
			}
		}
	}
	else {
		warn "can't open: $path";
	}
	return $title;
}

#------------------------------------------------------------------------------------------------------------
#
#	Sair kako log index
#	-------------------------------------------------------------------------------------
#	@param	$Sys	MELKOR
#	@param	$Page	THORIN
#	@param	$Banner	DENETHOR
#	@param	$pInfo	saída informação arranjo
#	@param	$base	keijiban top path
#	@param	$path	index saída path
#	@param	$Set	SETTING
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub OutputIndex
{
	
	my ($Sys, $Page, $Banner, $pInfo, $base, $path, $Set) = @_;
	
	my $cgipath	= $Sys->Get('CGIPATH');
	
	require './module/legolas.pl';
	my $Caption = LEGOLAS->new;
	$Caption->Load($Sys, 'META');
	
	my $version = $Sys->Get('VERSION');
	my $bbsRoot = $Sys->Get('CGIPATH') . '/' . $Sys->Get('BBSPATH') . '/'. $Sys->Get('BBS');
	my $board = $Sys->Get('BBS');
	
	$Page->Print(<<HTML);
<!DOCTYPE html>
<html lang="pt">
<head>

 <meta http-equiv="Content-Type" content="text/html;charset=UTF-8">

HTML
	
	$Caption->Print($Page, undef);
	
	$Page->Print(<<HTML);
 <title>Kako log armazém - $board$path</title>

</head>
<!--nobanner-->
<body>
HTML
	
	# kokuchi coluna saída
	$Banner->Print($Page, 100, 2, 0) if ($Sys->Get('BANNER') & 5);
	
	$Page->Print(<<HTML);

<h1 align="center" style="margin-bottom:0.2em;">Kako log armazém</h1>
<h2 align="center" style="margin-top:0.2em;">$board</h2>

<table border="1">
 <tr>
  <th>KEY</th>
  <th>subject</th>
  <th>date</th>
 </tr>
HTML
	
	foreach (@$pInfo) {
		my @elem = split(/<>/, $_, -1);
		
		# Subfolder informação
		if ($elem[0] eq '0') {
			$Page->Print(" <tr>\n  <td>Directory</td>\n  <td><a href=\"$elem[3]/\">");
			$Page->Print("$elem[3]</a></td>\n  <td>-</td>\n </tr>\n");
		}
		# Kako log informação
		else {
			$Page->Print(" <tr>\n  <td>$elem[0]</td>\n  <td><a href=\"$elem[0].html\">");
			$Page->Print("$elem[1]</a></td>\n  <td>$elem[2]</td>\n </tr>\n");
		}
	}
	$Page->Print("</table>\n\n<hr>\n");
	$Page->Print(<<HTML);

<a href="$bbsRoot/">■Voltar ao keijiban■</a> | <a href="$bbsRoot/kako/">■Voltar ao kako log top■</a> | <a href="../">■Voltar um para cima■</a>

<hr>

<div align="right">
$version
</div>
</body>
</html>
HTML
	
	# Sair index.html
	$Page->Flush(1, 0666, "$base/kako$path/index.html");
}

#============================================================================================================
#	Module terminação
#============================================================================================================
1;
