<?php
/* SEPA – Ô "Hiển thị trên site" khi viết bài.
   Tick tên miền nào thì bài hiện ở site vệ tinh đó (satellites/ trong repo xeap).
   Các site vệ tinh đọc qua REST: /wp-json/wp/v2/sepa_site và /wp-json/wp/v2/posts?sepa_site=<id>.
   Tắt snippet thì ô chọn biến mất; site vệ tinh vẫn lấy bài theo chuyên mục/thẻ như cũ. */

add_action( 'init', function () {
	register_taxonomy( 'sepa_site', 'post', array(
		'labels'            => array(
			'name'          => 'Hiển thị trên site',
			'singular_name' => 'Site vệ tinh',
			'menu_name'     => 'Site vệ tinh',
			'all_items'     => 'Tất cả site',
			'add_new_item'  => 'Thêm site',
			'edit_item'     => 'Sửa site',
		),
		'hierarchical'      => true,  // hiện dạng ô tick như Chuyên mục
		'public'            => false, // không tạo trang lưu trữ trên sepa.org.vn
		'show_ui'           => true,
		'show_admin_column' => true,
		'show_in_rest'      => true,
		'rest_base'         => 'sepa_site',
		'rewrite'           => false,
		'capabilities'      => array(
			'manage_terms' => 'manage_categories',
			'edit_terms'   => 'manage_categories',
			'delete_terms' => 'manage_categories',
			'assign_terms' => 'edit_posts',
		),
	) );

	// Tạo sẵn danh sách site một lần. Thêm site mới: Bài viết → Site vệ tinh.
	if ( get_option( 'sepa_site_terms_v1' ) ) {
		return;
	}
	$domains = array(
		'roboticschampionship.vn',
		'internationalroboticscompetition.vn',
		'roboticsforgood.vn',
		'darwinstem.vn',
		'stembansacviet.vn',
		'apistem.vn',
		'phuongmyloc.vn',
	);
	foreach ( $domains as $domain ) {
		if ( ! term_exists( $domain, 'sepa_site' ) ) {
			wp_insert_term( $domain, 'sepa_site', array( 'slug' => sanitize_title( str_replace( '.', '-', $domain ) ) ) );
		}
	}
	update_option( 'sepa_site_terms_v1', 1 );
}, 5 );
