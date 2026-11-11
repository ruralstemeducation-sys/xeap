<?php
/* SEPA – Thư viện album ảnh (/media).
   Shortcode [sepa_media_albums]: liệt kê mọi trang con của trang /media (mỗi trang con = một album sự kiện),
   mới nhất trước, nhóm theo năm. Ảnh bìa = ảnh đại diện của album, mô tả = đoạn tóm tắt (excerpt).
   Thêm album mới: tạo trang, chọn "Trang cha" = Media, đặt ảnh đại diện + tóm tắt, ngày đăng = ngày sự kiện. */

add_action( 'init', function () {
	add_post_type_support( 'page', 'excerpt' );
} );

add_shortcode( 'sepa_media_albums', function ( $atts ) {
	$atts   = shortcode_atts( array( 'parent' => 0 ), $atts );
	$parent = (int) $atts['parent'];
	if ( ! $parent ) {
		$media  = get_page_by_path( 'media' );
		$parent = $media ? $media->ID : get_the_ID();
	}
	$albums = get_pages( array(
		'parent'      => $parent,
		'sort_column' => 'post_date',
		'sort_order'  => 'DESC',
		'post_status' => 'publish',
	) );
	if ( ! $albums ) {
		return '<p class="sepa-albums-empty">Album đang được cập nhật.</p>';
	}

	ob_start();
	?>
	<style>
	.sepa-albums{--navy:#0b2a4a;--accent:#f39200;--ink:#1d2733;--muted:#5b6878;--line:#e3e8ee;--soft:#f5f8fb}
	.sepa-albums .sa-year{display:flex;align-items:center;gap:12px;font-size:20px;font-weight:800;color:var(--navy);margin:34px 0 14px}
	.sepa-albums .sa-year::after{content:"";flex:1;height:1px;background:var(--line)}
	.sepa-albums .sa-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}
	.sepa-albums .sa-card{display:flex;flex-direction:column;background:#fff;border:1px solid var(--line);border-radius:14px;overflow:hidden;text-decoration:none;color:var(--ink);transition:box-shadow .2s,transform .2s}
	.sepa-albums .sa-card:hover{box-shadow:0 10px 28px rgba(11,42,74,.12);transform:translateY(-3px)}
	.sepa-albums .sa-cover{position:relative;aspect-ratio:4/3;background:var(--soft);overflow:hidden}
	.sepa-albums .sa-cover img{position:absolute;inset:0;width:100%!important;height:100%!important;max-width:none;margin:0!important;border-radius:0;object-fit:cover;display:block;transition:transform .35s}
	.sepa-albums .sa-card:hover .sa-cover img{transform:scale(1.04)}
	.sepa-albums .sa-count{position:absolute;right:10px;bottom:10px;background:rgba(11,42,74,.85);color:#fff;font-size:12.5px;font-weight:700;padding:4px 10px;border-radius:999px}
	.sepa-albums .sa-body{padding:14px 16px 18px;display:flex;flex-direction:column;gap:6px;flex:1}
	.sepa-albums .sa-date{font-size:12.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--accent)}
	.sepa-albums .sa-title{font-size:17px;line-height:1.4;font-weight:800;color:var(--navy);margin:0}
	.sepa-albums .sa-desc{font-size:14.5px;line-height:1.55;color:var(--muted);margin:0;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
	.sepa-albums .sa-more{margin-top:auto;padding-top:6px;font-size:14px;font-weight:700;color:var(--navy)}
	@media (max-width:900px){.sepa-albums .sa-grid{grid-template-columns:1fr 1fr;gap:16px}}
	@media (max-width:560px){.sepa-albums .sa-grid{grid-template-columns:1fr}}
	</style>
	<div class="sepa-albums">
	<?php
	$year = null;
	foreach ( $albums as $a ) {
		$y = get_the_date( 'Y', $a );
		if ( $y !== $year ) {
			if ( null !== $year ) {
				echo '</div>';
			}
			$year = $y;
			echo '<h2 class="sa-year">' . esc_html( $y ) . '</h2><div class="sa-grid">';
		}
		$count = preg_match_all( '/wp-image-\d+/', $a->post_content );
		$title = preg_replace( '/^Album ảnh\s*/u', '', get_the_title( $a ) );
		$thumb = get_the_post_thumbnail( $a, 'medium_large', array( 'loading' => 'lazy', 'alt' => esc_attr( $title ) ) );
		?>
		<a class="sa-card" href="<?php echo esc_url( get_permalink( $a ) ); ?>">
			<div class="sa-cover"><?php echo $thumb; ?><?php if ( $count ) : ?><span class="sa-count"><?php echo (int) $count; ?> ảnh</span><?php endif; ?></div>
			<div class="sa-body">
				<span class="sa-date"><?php echo esc_html( get_the_date( 'd/m/Y', $a ) ); ?></span>
				<h3 class="sa-title"><?php echo esc_html( $title ); ?></h3>
				<?php if ( has_excerpt( $a ) ) : ?><p class="sa-desc"><?php echo esc_html( get_the_excerpt( $a ) ); ?></p><?php endif; ?>
				<span class="sa-more">Xem album →</span>
			</div>
		</a>
		<?php
	}
	echo '</div></div>';
	return ob_get_clean();
} );

/* Album đăng lần đầu ở địa chỉ gốc, sau chuyển vào /media/... – giữ link cũ */
add_action( 'template_redirect', function () {
	if ( is_404() && preg_match( '#^/(album-[a-z0-9-]+)/?$#', wp_parse_url( $_SERVER['REQUEST_URI'], PHP_URL_PATH ), $m ) ) {
		$page = get_page_by_path( 'media/' . $m[1] );
		if ( $page ) {
			wp_safe_redirect( get_permalink( $page ), 301 );
			exit;
		}
	}
} );
