#============================================================================================================
#
#	セッション管理モジュール
#
#============================================================================================================

#============================================================================================================
#
#	セッションマネージャパッケージ
#
#============================================================================================================
package SessionManager;

use strict;
#use warnings;

#------------------------------------------------------------------------------------------------------------
#
#	セッションの取得
#	-------------------------------------------------------------------------------------
#	@param	なし
#	@return	Sessionオブジェクト
#
#------------------------------------------------------------------------------------------------------------
sub getSession
{
	
	my $session = new Session;
	my $id = createSessionID();
	my $filePath = "./info/session/$id";
	my $check = 1;
	
	# セッション情報ファイルが存在する場合はそれを読み込む
	if (open(my $fh, '<', $filePath)) {
		flock($fh, 2);
		my @lines = <$fh>;
		close($fh);
		map { s/[\r\n]+\z// } @lines;
		
		foreach (@lines) {
			# 1行目(セッション開始時間)を取得
			if ($check) {
				$check = 0;
				$session->setId($_);
				if (time - $_ > 3600) {
					$session->setId(time);
					last;
				}
			# 2行目以降(セッション属性値)を取得
			}
			else {
				my ($key, $value) = split(/=/, $_);
				$value =~ s/&equal;/=/g;
				$session->setAttribute($key, $value);
			}
		}
	# セッション情報ファイルが存在しない場合は空ファイルを作成する
	}
	else {
		if (!-e './info/session' || !-d './info/session') {
			require './module/earendil.pl';
			EARENDIL::CreateDirectory('./info/session', 0770);
		}
		open(my $fh, '>', $filePath);
		close($fh);
		$session->setId(time);
	}
	return $session;
}

#------------------------------------------------------------------------------------------------------------
#
#	セッションの保存
#	-------------------------------------------------------------------------------------
#	@param	$session	Sessionオブジェクト
#	@return	なし
#
#------------------------------------------------------------------------------------------------------------
sub setSession
{
	
	my ($session) = @_;
	
	my $id = createSessionID($ENV{'REMOTE_ADDR'});
	my $filePath = "./info/session/$id";
	
	if (open(my $fh, '+<', $filePath)) {
		flock($fh, 2);
		seek($fh, 0, 0);
		binmode($fh);
		
		print $fh $session->getId() . "\n";
		foreach my $key (keys %{$session->{'ATTRIBUTE'}}) {
			my $value = $session->getAttribute($key);
			$value =~ s/=/&equal;/g;
			print $fh "$key=$value\n";
		}
		
		truncate($fh, tell($fh));
		close($fh);
	}
}

#------------------------------------------------------------------------------------------------------------
#
#	セッションの削除
#	-------------------------------------------------------------------------------------
#	@param	なし
#	@return	なし
#
#------------------------------------------------------------------------------------------------------------
sub removeSession
{
	
	my $id = createSessionID($ENV{'REMOTE_ADDR'});
	my $filePath = "./info/session/$id";
	
	unlink $filePath;
}

#------------------------------------------------------------------------------------------------------------
#
#	セッションIDの生成
#	-------------------------------------------------------------------------------------
#	@param	なし
#	@return	セッションID
#
#------------------------------------------------------------------------------------------------------------
sub createSessionID
{
	
	my $key = $ENV{'REMOTE_ADDR'};
	$key =~ s/\.//g;
	$key = substr($ENV{'REMOTE_ADDR'}, -8);
	
	return substr(crypt($key, substr(crypt($key, 'ZC'), -2)), -26);
}

#============================================================================================================
#
#	セッションオブジェクトパッケージ
#
#============================================================================================================
package Session;

use strict;
#use warnings;

#------------------------------------------------------------------------------------------------------------
#
#	コンストラクタ
#	-------------------------------------------------------------------------------------
#	@param	なし
#	@return	セッションオブジェクト
#
#------------------------------------------------------------------------------------------------------------
sub new
{
	my $class = shift;
	
	my $obj = {
		'ID'		=> undef,
		'ATTRIBUTE'	=> undef,
	};
	bless $obj, $class;
	
	return $obj;
}

#------------------------------------------------------------------------------------------------------------
#
#	デストラクタ
#	-------------------------------------------------------------------------------------
#	@param	なし
#	@return	なし
#
#------------------------------------------------------------------------------------------------------------
sub DESTROY
{
	my $this = shift;
	
	if (defined $this->{'ID'}) {
		SessionManager::setSession($this);
	}
}

#------------------------------------------------------------------------------------------------------------
#
#	属性設定
#	-------------------------------------------------------------------------------------
#	@param	$key	属性キー
#	@param	$value	属性値
#	@return	なし
#
#------------------------------------------------------------------------------------------------------------
sub setAttribute
{
	my $this = shift;
	my ($key, $value) = @_;
	
	$this->{'ATTRIBUTE'}->{$key} = $value;
}

#------------------------------------------------------------------------------------------------------------
#
#	属性取得
#	-------------------------------------------------------------------------------------
#	@param	$key	属性キー
#	@return	属性値
#
#------------------------------------------------------------------------------------------------------------
sub getAttribute
{
	my $this = shift;
	my ($key) = @_;
	
	return $this->{'ATTRIBUTE'}->{$key};
}

#------------------------------------------------------------------------------------------------------------
#
#	属性削除
#	-------------------------------------------------------------------------------------
#	@param	$key	属性キー
#	@return	なし
#
#------------------------------------------------------------------------------------------------------------
sub removeAttribute
{
	my $this = shift;
	my ($key) = @_;
	
	delete $this->{'ATTRIBUTE'}->{$key};
}

#------------------------------------------------------------------------------------------------------------
#
#	ID設定
#	-------------------------------------------------------------------------------------
#	@param	$id	ID
#	@return	なし
#
#------------------------------------------------------------------------------------------------------------
sub setId
{
	my $this = shift;
	my ($id) = @_;
	$this->{'ID'} = $id;
}

#------------------------------------------------------------------------------------------------------------
#
#	ID取得
#	-------------------------------------------------------------------------------------
#	@param	なし
#	@return	ID
#
#------------------------------------------------------------------------------------------------------------
sub getId
{
	my $this = shift;
	return $this->{'ID'};
}

#============================================================================================================
#	Module END
#============================================================================================================
1;
