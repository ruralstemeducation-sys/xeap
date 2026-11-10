<?php
/* SEPA – Sửa nhanh sau rà soát website (11/2026).
   Gồm: bảo mật cơ bản, tiêu đề trang gọn, chuyển hướng trang trùng, canonical + dữ liệu cấu trúc,
   trang chủ (khu mạng xã hội gọn, mỗi trang một thẻ H1). Tắt snippet này để hoàn tác toàn bộ. */

if ( ! function_exists( 'sepa_qf_is_en' ) ) {
	function sepa_qf_is_en() {
		return function_exists( 'pll_current_language' ) && 'en' === pll_current_language();
	}
}

/* 1. Bảo mật: không công khai danh sách tài khoản, thêm header bảo mật */
add_filter( 'rest_endpoints', function ( $endpoints ) {
	if ( ! is_user_logged_in() ) {
		unset( $endpoints['/wp/v2/users'], $endpoints['/wp/v2/users/(?P<id>[\d]+)'] );
	}
	return $endpoints;
} );
add_filter( 'wp_sitemaps_add_provider', function ( $provider, $name ) {
	return 'users' === $name ? false : $provider;
}, 10, 2 );
add_action( 'template_redirect', function () {
	if ( ! is_user_logged_in() && ( is_author() || isset( $_GET['author'] ) ) ) {
		wp_safe_redirect( home_url( '/' ), 301 );
		exit;
	}
}, 0 );
add_action( 'send_headers', function () {
	if ( function_exists( 'header_remove' ) ) {
		header_remove( 'X-Powered-By' );
	}
	header( 'X-Content-Type-Options: nosniff' );
	header( 'X-Frame-Options: SAMEORIGIN' );
	header( 'Referrer-Policy: strict-origin-when-cross-origin' );
	header( 'Strict-Transport-Security: max-age=31536000' );
	header( 'Permissions-Policy: camera=(), microphone=(), geolocation=()' );
} );

/* 2. Tiêu đề trang: "Tên trang | SEPA" thay cho đuôi dài bị Google cắt */
add_filter( 'document_title_separator', function () {
	return '|';
} );
add_filter( 'document_title_parts', function ( $parts ) {
	if ( is_front_page() ) {
		return array( 'title' => sepa_qf_is_en() ? 'SEPA – STEM Education Promotion Alliance' : 'SEPA – Liên minh Thúc đẩy Giáo dục STEM' );
	}
	if ( isset( $parts['site'] ) ) {
		$parts['site'] = 'SEPA';
	}
	unset( $parts['tagline'] );
	return $parts;
}, 20 );

/* 3. Chuyển hướng 301 các trang trùng hoặc rỗng về trang chuẩn */
add_action( 'template_redirect', function () {
	$path = trim( rawurldecode( (string) wp_parse_url( $_SERVER['REQUEST_URI'], PHP_URL_PATH ) ), '/' );
	$map  = array(
		'sang-lap.htm'                                => '/sang-lap',
		'gioi-thieu/doi-ngu-sang-lap/sang-lap-va-dieu-hanh' => '/gioi-thieu/doi-ngu-sang-lap',
		'lang-chanh'                                  => '/lang-chanh-thanh-hoa',
		'dai-su-stem-hoc-sinh-2'                      => '/dai-su-stem-hoc-sinh-2/dai-su-stem-2',
		'sepalienminh'                                => '/gioi-thieu',
	);
	if ( isset( $map[ $path ] ) ) {
		wp_safe_redirect( home_url( $map[ $path ] ), 301 );
		exit;
	}
}, 0 );

/* 4. Canonical cho trang chủ và chuyên mục (bài và trang đã có sẵn từ WordPress) + dữ liệu cấu trúc Organization */
add_action( 'wp_head', function () {
	if ( defined( 'WPSEO_VERSION' ) || defined( 'RANK_MATH_VERSION' ) ) {
		return;
	}
	$url = '';
	if ( is_front_page() ) {
		$url = function_exists( 'pll_home_url' ) ? pll_home_url() : home_url( '/' );
	} elseif ( is_category() || is_tag() ) {
		$url = get_term_link( get_queried_object() );
		if ( is_paged() && ! is_wp_error( $url ) ) {
			$url = trailingslashit( $url ) . 'page/' . (int) get_query_var( 'paged' );
		}
		/* Mô tả cho trang danh sách tin: lấy mô tả chuyên mục nếu có, không thì dùng câu chung */
		$term = get_queried_object();
		$desc = $term && ! empty( $term->description ) ? wp_strip_all_tags( $term->description ) : '';
		if ( '' === $desc ) {
			$name = $term ? $term->name : '';
			$desc = sepa_qf_is_en()
				? sprintf( '%s from SEPA – STEM Education Promotion Alliance: programmes, competitions and stories on STEM, robotics and AI education in Vietnam.', $name )
				: sprintf( '%s của SEPA – Liên minh Thúc đẩy Giáo dục STEM: chương trình, giải đấu và câu chuyện giáo dục STEM, Robotics, AI tại Việt Nam.', $name );
		}
		if ( is_paged() ) {
			$desc .= sepa_qf_is_en() ? ' Page ' . (int) get_query_var( 'paged' ) . '.' : ' Trang ' . (int) get_query_var( 'paged' ) . '.';
		}
		echo '<meta name="description" content="' . esc_attr( $desc ) . '">' . "\n";
	}
	if ( $url && ! is_wp_error( $url ) ) {
		echo '<link rel="canonical" href="' . esc_url( $url ) . '">' . "\n";
	}
	if ( is_front_page() ) {
		$org = array(
			'@context'      => 'https://schema.org',
			'@type'         => 'Organization',
			'name'          => sepa_qf_is_en() ? 'STEM Education Promotion Alliance (SEPA)' : 'Liên minh Thúc đẩy Giáo dục STEM (SEPA)',
			'alternateName' => array( 'SEPA', 'STEM Education Promotion Alliance', 'Liên minh Thúc đẩy Giáo dục STEM' ),
			'legalName'     => 'Công ty TNHH Liên Minh Thúc đẩy Giáo dục STEM',
			'taxID'         => '0601247587',
			'slogan'        => 'Quality STEM Education for All',
			'url'           => 'https://sepa.org.vn/',
			'logo'          => 'https://sepa.org.vn/wp-content/uploads/2026/11/sepa-logo-horizontal-blue.png',
			'email'         => 'sepa@sepa.org.vn',
			'telephone'     => '+84817750229',
			'address'       => array(
				'@type'           => 'PostalAddress',
				'streetAddress'   => 'Thôn Cao Đài 2, Phường Mỹ Lộc',
				'addressRegion'   => 'Ninh Bình',
				'addressCountry'  => 'VN',
			),
			'sameAs'        => array(
				'https://www.facebook.com/sepa.org.vn/',
				'https://www.youtube.com/@STEMEducationPromotion',
				'https://www.linkedin.com/company/sepastem/',
			),
		);
		echo '<script type="application/ld+json">' . wp_json_encode( $org, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES ) . '</script>' . "\n";
	}
}, 2 );

/* 5. Trang chủ: một thẻ H1 duy nhất, khu "Kết nối cùng SEPA" gọn thay cho 4 khung lớn */
add_action( 'template_redirect', function () {
	if ( is_admin() || ! is_front_page() ) {
		return;
	}
	ob_start( function ( $html ) {
		if ( false === strpos( $html, 'sepa-fp-slide-copy' ) ) {
			return $html;
		}
		$en = sepa_qf_is_en();

		/* 5a. Tiêu đề slide dùng h2 (giữ nguyên kiểu chữ), thêm H1 tên tổ chức cho máy tìm kiếm và trình đọc màn hình */
		$html = preg_replace( '#(<div class="sepa-fp-slide-copy">\s*<span class="sepa-fp-kicker">[^<]*</span>\s*)<h1>(.*?)</h1>#s', '$1<h2 class="sepa-fp-slide-h">$2</h2>', $html );
		$h1   = '<h1 class="sepa-qf-sr">' . ( $en ? 'SEPA – STEM Education Promotion Alliance: Quality STEM Education for All' : 'SEPA – Liên minh Thúc đẩy Giáo dục STEM: Giáo dục STEM chất lượng cho mọi trẻ em' ) . '</h1>';
		$pos  = strpos( $html, '<section class="sepa-fp-hero' );
		if ( false === $pos ) {
			$pos = strpos( $html, 'sepa-fp-hero' );
			$pos = false === $pos ? false : strrpos( substr( $html, 0, $pos ), '<' );
		}
		if ( false !== $pos ) {
			$html = substr_replace( $html, $h1, $pos, 0 );
		}

		/* 5b. Thay khu mạng xã hội */
		$channels = array(
			array( 'https://www.facebook.com/sepa.org.vn/', 'fb', 'SEPA', 'Facebook' ),
			array( 'https://www.facebook.com/roboticsforgoodvn/', 'fb', 'Robotics for Good Vietnam', 'Facebook' ),
			array( 'https://www.facebook.com/nasaspaceappsvn/', 'fb', 'NASA Space Apps Vietnam', 'Facebook' ),
			array( 'https://www.youtube.com/@STEMEducationPromotion', 'yt', 'SEPA', 'YouTube' ),
			array( 'https://www.linkedin.com/company/sepastem/', 'li', 'SEPA', 'LinkedIn' ),
		);
		$icons = array(
			'fb' => '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13.5 21v-7.5h2.5l.4-3h-2.9V8.6c0-.9.3-1.5 1.5-1.5h1.5V4.4c-.3 0-1.2-.1-2.2-.1-2.2 0-3.7 1.3-3.7 3.8v2.4H8v3h2.6V21z"/></svg>',
			'yt' => '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21.6 7.2a2.5 2.5 0 0 0-1.8-1.8C18.2 5 12 5 12 5s-6.2 0-7.8.4A2.5 2.5 0 0 0 2.4 7.2 26 26 0 0 0 2 12a26 26 0 0 0 .4 4.8 2.5 2.5 0 0 0 1.8 1.8C5.8 19 12 19 12 19s6.2 0 7.8-.4a2.5 2.5 0 0 0 1.8-1.8A26 26 0 0 0 22 12a26 26 0 0 0-.4-4.8zM10 15V9l5.2 3z"/></svg>',
			'li' => '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.9 8.8H3.6V20h3.3zM5.2 3.5a1.9 1.9 0 1 0 0 3.9 1.9 1.9 0 0 0 0-3.9zM20.4 13.6c0-3-1.6-5-4.3-5a3.7 3.7 0 0 0-3.3 1.8V8.8H9.6V20h3.3v-5.5c0-1.5.3-2.9 2.1-2.9s1.9 1.7 1.9 3V20h3.4z"/></svg>',
		);
		$items = '';
		foreach ( $channels as $c ) {
			$items .= '<li><a class="sepa-ss-link is-' . $c[1] . '" href="' . esc_url( $c[0] ) . '" target="_blank" rel="noopener">'
				. '<span class="sepa-ss-ic">' . $icons[ $c[1] ] . '</span>'
				. '<span class="sepa-ss-tx"><b>' . esc_html( $c[2] ) . '</b><small>' . esc_html( $c[3] ) . '</small></span></a></li>';
		}
		$strip = '<section class="sepa-social-strip" aria-label="' . ( $en ? 'Follow SEPA' : 'Kết nối cùng SEPA' ) . '"><div class="container sepa-ss-inner">'
			. '<div class="sepa-ss-text"><h2>' . ( $en ? 'Follow SEPA' : 'Kết nối cùng SEPA' ) . '</h2><p>'
			. ( $en ? 'News, photos and stories from our STEM programmes.' : 'Tin tức, hình ảnh và câu chuyện từ các chương trình STEM của SEPA.' )
			. '</p></div><ul class="sepa-ss-list">' . $items . '</ul></div></section>';
		$html = preg_replace( '#<section class="section section-light sepa-fp-social-section">.*?</section>#s', $strip, $html, 1 );

		$css = '<style id="sepa-quickfix">'
			. '.sepa-qf-sr{position:absolute!important;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}'
			. '.sepa-fp-slide-copy .sepa-fp-slide-h{font-size:38px;font-weight:700;line-height:1.18;letter-spacing:-.02em;color:#101827;margin:0}'
			. '@media (max-width:1024px){.sepa-fp-slide-copy .sepa-fp-slide-h{font-size:28px}}'
			. '.sepa-social-strip{background:#f6f8ff;padding:44px 0;border-top:1px solid #e6eaf5}'
			. '.sepa-ss-inner{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:20px 32px}'
			. '.sepa-ss-text h2{margin:0 0 4px;font-size:24px;line-height:1.25;color:#101827}'
			. '.sepa-ss-text p{margin:0;color:#56607a;font-size:15px}'
			. '.sepa-ss-list{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:10px}'
			. '.sepa-ss-link{display:flex;align-items:center;gap:10px;padding:9px 16px 9px 9px;background:#fff;border:1px solid #e1e6f2;border-radius:999px;text-decoration:none;color:#101827;transition:border-color .15s,box-shadow .15s}'
			. '.sepa-ss-link:hover,.sepa-ss-link:focus-visible{border-color:#9fb4e8;box-shadow:0 4px 14px rgba(16,24,39,.08)}'
			. '.sepa-ss-ic{width:34px;height:34px;border-radius:50%;display:grid;place-items:center;flex:none}'
			. '.sepa-ss-ic svg{width:18px;height:18px;fill:#fff}'
			. '.is-fb .sepa-ss-ic{background:#1877f2}.is-yt .sepa-ss-ic{background:#ff0033}.is-li .sepa-ss-ic{background:#0a66c2}'
			. '.sepa-ss-tx{display:flex;flex-direction:column;line-height:1.2}'
			. '.sepa-ss-tx b{font-size:14px;font-weight:600}.sepa-ss-tx small{font-size:12px;color:#56607a}'
			. '@media (max-width:640px){.sepa-social-strip{padding:32px 0}.sepa-ss-list{width:100%}.sepa-ss-list li{flex:1 1 100%}.sepa-ss-link{min-height:48px}}'
			. '</style>';
		$html = str_replace( '</head>', $css . '</head>', $html );
		return $html;
	} );
}, 2 );

/* 6. Trang /sang-lap: chữ sáng trên nền xanh đậm cho dễ đọc */
add_action( 'wp_head', function () {
	if ( ! is_page( 22325 ) ) {
		return;
	}
	echo '<style id="sepa-qf-sanglap">.page-id-22325 .elementor-element-174801db,.page-id-22325 .elementor-element-174801db p,.page-id-22325 .elementor-widget-text-editor p{color:#e4ecf6!important}.page-id-22325 .elementor-drop-cap-letter{color:#f3a53a!important}</style>' . "\n";
}, 99 );
