<?php
/* SEPA – Đếm lượt truy cập bằng Google Analytics 4 (11/2026). Chạy: "Run snippet everywhere".
   Cùng cách làm với eventstem.com (js/stats.js) và Davilearn. Tắt snippet này để ngừng đếm.
   - Chỉ khách và tài khoản thường được đếm; quản trị / biên tập viên đang đăng nhập không bị đếm.
   - Địa chỉ trang gửi đi chỉ giữ tham số nguồn (utm_*, ref) và mã trang (p, page_id, cat, lang);
     bỏ mọi tham số khác (vd. ?s= từ khoá tìm kiếm). Tắt Google signals + quảng cáo cá nhân hoá.
   - Điền mã luồng GA4 (G-…) của sepa.org.vn vào SEPA_GA4_ID. Mã này không bí mật.
   Snippet #40 trên web (tạo 21/11/2026, đang tắt cho tới khi có mã G-…). */

if ( ! defined( 'SEPA_GA4_ID' ) ) {
	define( 'SEPA_GA4_ID', '' );
}

add_action( 'wp_head', function () {
	$id = SEPA_GA4_ID;
	if ( ! preg_match( '/^G-[A-Z0-9]{4,}$/', $id ) ) {
		return;
	}
	if ( is_user_logged_in() && current_user_can( 'edit_posts' ) ) {
		return;
	}
	if ( is_preview() || is_customize_preview() ) {
		return;
	}
	?>
<script async src="https://www.googletagmanager.com/gtag/js?id=<?php echo esc_attr( $id ); ?>"></script>
<script>
(function () {
	var KEEP = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'ref', 'p', 'page_id', 'cat', 'lang'];
	var HOSTS = ['sepa.org.vn', 'www.sepa.org.vn'];
	function q(search) {
		var out = [];
		String(search || '').replace(/^\?/, '').split('&').forEach(function (kv) {
			if (!kv) return;
			var k = '';
			try { k = decodeURIComponent(kv.split('=')[0] || ''); } catch (e) { return; }
			if (KEEP.indexOf(k) >= 0) out.push(kv);
		});
		return out.length ? '?' + out.join('&') : '';
	}
	function ref(r) {
		var m = String(r || '').match(/^(https?:\/\/([^\/?#]+))([^?#]*)(\?[^#]*)?/);
		if (!m) return '';
		return m[1] + m[3] + (HOSTS.indexOf(m[2]) >= 0 ? q(m[4]) : '');
	}
	window.dataLayer = window.dataLayer || [];
	window.gtag = function () { window.dataLayer.push(arguments); };
	gtag('js', new Date());
	gtag('config', <?php echo wp_json_encode( $id ); ?>, {
		page_location: location.origin + location.pathname + q(location.search),
		page_referrer: ref(document.referrer),
		allow_google_signals: false,
		allow_ad_personalization_signals: false
	});
})();
</script>
	<?php
}, 5 );
