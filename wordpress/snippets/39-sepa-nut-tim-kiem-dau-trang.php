<?php
/* SEPA – Nút tìm kiếm trên đầu trang (header Elementor 21661).
   Thêm biểu tượng kính lúp cạnh menu chính (máy tính) và cạnh nút menu ba gạch (điện thoại).
   Bấm vào mở ô tìm kiếm phủ trên trang; tìm theo ngôn ngữ đang xem (Polylang: /?s= hoặc /en/?s=).
   Phím tắt: "/" hoặc Ctrl+K để mở, Esc để đóng. Tắt snippet này để hoàn tác. */

add_action( 'wp_footer', function () {
	if ( is_admin() ) {
		return;
	}
	$en     = function_exists( 'pll_current_language' ) && 'en' === pll_current_language();
	$action = function_exists( 'pll_home_url' ) ? pll_home_url() : home_url( '/' );
	$t      = $en
		? array( 'btn' => 'Search', 'title' => 'Search SEPA', 'ph' => 'Programmes, news, competitions…', 'go' => 'Search', 'close' => 'Close', 'hint' => 'Popular:' )
		: array( 'btn' => 'Tìm kiếm', 'title' => 'Tìm kiếm trên SEPA', 'ph' => 'Chương trình, tin tức, giải đấu…', 'go' => 'Tìm', 'close' => 'Đóng', 'hint' => 'Gợi ý:' );
	$tags   = $en
		? array( 'Robotics', 'NASA Space Apps', 'CREST Awards', 'STEM' )
		: array( 'Robotics', 'NASA Space Apps', 'CREST Awards', 'Đại sứ STEM' );
	$icon   = '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false"><circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke="currentColor" stroke-width="2.2"/><path d="m15.5 15.5 5 5" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>';
	$q      = get_search_query();

	$chips = '';
	foreach ( $tags as $tag ) {
		$chips .= '<a href="' . esc_url( add_query_arg( 's', rawurlencode( $tag ), $action ) ) . '">' . esc_html( $tag ) . '</a>';
	}
	?>
<template id="sepa-search-btn-tpl"><button type="button" class="sepa-search-btn" aria-label="<?php echo esc_attr( $t['btn'] ); ?>" aria-haspopup="dialog" aria-controls="sepa-search-dlg" title="<?php echo esc_attr( $t['btn'] ); ?> ( / )"><?php echo $icon; // phpcs:ignore ?></button></template>
<dialog id="sepa-search-dlg" class="sepa-search-dlg" aria-label="<?php echo esc_attr( $t['title'] ); ?>">
	<form role="search" method="get" action="<?php echo esc_url( $action ); ?>" class="sepa-search-form">
		<label for="sepa-search-q" class="sepa-search-title"><?php echo esc_html( $t['title'] ); ?></label>
		<div class="sepa-search-row">
			<span class="sepa-search-ic"><?php echo $icon; // phpcs:ignore ?></span>
			<input id="sepa-search-q" type="search" name="s" value="<?php echo esc_attr( $q ); ?>" placeholder="<?php echo esc_attr( $t['ph'] ); ?>" autocomplete="off" required>
			<button type="submit" class="sepa-search-go"><?php echo esc_html( $t['go'] ); ?></button>
		</div>
		<p class="sepa-search-tags"><span><?php echo esc_html( $t['hint'] ); ?></span><?php echo $chips; // phpcs:ignore ?></p>
		<button type="button" class="sepa-search-x" aria-label="<?php echo esc_attr( $t['close'] ); ?>"><svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg></button>
	</form>
</dialog>
<style id="sepa-search-css">
.sepa-search-slot{display:flex;align-items:center;justify-content:flex-end;gap:6px;width:100%}
.sepa-search-slot>.elementor-widget-nav-menu{flex:0 1 auto;width:auto;min-width:0;margin-bottom:0!important}
.sepa-search-btn{flex:none;width:40px;height:40px;padding:0;margin:0;border:1px solid #d8e2ee;border-radius:50%;background:#fff;color:#0372AE;display:inline-grid;place-items:center;cursor:pointer;transition:background .15s,color .15s,border-color .15s}
.sepa-search-btn:hover,.sepa-search-btn:focus-visible{background:#0372AE;border-color:#0372AE;color:#fff}
.sepa-search-btn:focus-visible{outline:2px solid #0372AE;outline-offset:2px}
.sepa-search-dlg{width:min(680px,calc(100% - 32px));max-width:none;margin:12vh auto auto;padding:0;border:0;border-radius:16px;background:#fff;color:#101827;box-shadow:0 24px 60px rgba(16,24,39,.28)}
.sepa-search-dlg::backdrop{background:rgba(10,20,40,.55);backdrop-filter:blur(2px)}
.sepa-search-form{position:relative;padding:24px 24px 20px;margin:0}
.sepa-search-title{display:block;margin:0 40px 14px 0;font-size:18px;font-weight:700;line-height:1.3;color:#101827}
.sepa-search-row{display:flex;align-items:center;gap:8px;padding:6px 6px 6px 14px;border:2px solid #d8e2ee;border-radius:12px;transition:border-color .15s}
.sepa-search-row:focus-within{border-color:#0372AE}
.sepa-search-ic{color:#7a8599;display:grid;place-items:center;flex:none}
.sepa-search-row input[type=search]{flex:1;min-width:0;border:0!important;outline:0;box-shadow:none!important;background:transparent;padding:8px 0!important;margin:0;font-size:17px;line-height:1.4;color:#101827}
.sepa-search-go{flex:none;border:0;border-radius:8px;background:#0372AE;color:#fff;font-size:15px;font-weight:600;padding:10px 18px;cursor:pointer;line-height:1.2}
.sepa-search-go:hover,.sepa-search-go:focus-visible{background:#025a8a}
.sepa-search-tags{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:14px 0 0;font-size:14px;color:#56607a}
.sepa-search-tags a{padding:5px 12px;border-radius:999px;background:#eef4fa;color:#0b4f7a;text-decoration:none}
.sepa-search-tags a:hover,.sepa-search-tags a:focus-visible{background:#dbe9f6}
.sepa-search-x{position:absolute;top:14px;right:14px;width:36px;height:36px;padding:0;border:0;border-radius:50%;background:transparent;color:#56607a;display:grid;place-items:center;cursor:pointer}
.sepa-search-x:hover,.sepa-search-x:focus-visible{background:#f0f2f6;color:#101827}
@media (max-width:640px){.sepa-search-dlg{margin-top:16px}.sepa-search-form{padding:20px 16px 16px}.sepa-search-go{padding:10px 14px}.sepa-search-row input[type=search]{font-size:16px}}
</style>
<script id="sepa-search-js">
(function(){
	var dlg=document.getElementById('sepa-search-dlg'),tpl=document.getElementById('sepa-search-btn-tpl');
	if(!dlg||!tpl||typeof dlg.showModal!=='function')return;
	var nav=document.querySelector('.elementor-location-header .elementor-widget-nav-menu');
	if(!nav||!nav.parentNode)return;
	var slot=nav.parentNode;
	slot.classList.add('sepa-search-slot');
	var btn=tpl.content.firstElementChild.cloneNode(true);
	slot.appendChild(btn);
	var input=document.getElementById('sepa-search-q'),last=null;
	function open(){last=document.activeElement;dlg.showModal();input.focus();input.select();}
	function close(){dlg.close();}
	btn.addEventListener('click',open);
	dlg.querySelector('.sepa-search-x').addEventListener('click',close);
	dlg.addEventListener('click',function(e){if(e.target===dlg)close();});
	dlg.addEventListener('keydown',function(e){if(e.key==='Escape'){e.preventDefault();close();}});
	dlg.addEventListener('close',function(){if(last&&last.focus)last.focus();});
	document.addEventListener('keydown',function(e){
		if(dlg.open)return;
		var t=e.target,typing=t&&(t.isContentEditable||/^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName));
		if((e.key==='/'&&!typing&&!e.ctrlKey&&!e.metaKey&&!e.altKey)||((e.ctrlKey||e.metaKey)&&(e.key==='k'||e.key==='K'))){e.preventDefault();open();}
	});
})();
</script>
	<?php
}, 20 );
