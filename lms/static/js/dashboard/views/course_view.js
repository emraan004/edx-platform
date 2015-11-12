;(function (define, accessibleModal) {
    'use strict';

    define(['jquery',
            'backbone',
            'underscore',
            'underscore.string',
            'text!templates/dashboard/course.underscore'],
        function ($,
                  Backbone,
                  _,
                  _s,
                  courseTemplate) {

            if (_.isUndefined(_s)) {
                _s = _.str;
            }

            var CourseView = Backbone.View.extend({
                tagName: 'li',
                className: 'course-item',
                template: _.template(courseTemplate),

                events: {
                    'click .action-more': 'toggleCourseActionsDropDown',
                    'click .action-unenroll': 'unEnroll',
                    'click .action-email-settings': 'emailSettings',
                    'click #upgrade-to-verified': 'upgradeToVerified',
                    'click #block-course-msg a[rel="leanModal"]': 'unRegisterBlockCourse'
                },

                initialize: function (options) {
                    this.listenTo(options.tabbedView, 'rendered', this.rendered);
                    this.settings = options.settings;

                    /* Mix non-conflicting functions from underscore.string
                     * (all but include, contains, and reverse) into the
                     * Underscore namespace
                     */
                    _.mixin(_s.exports());
                },

                render: function () {
                    this.$el.html(this.template({model: this.model.attributes, settings: this.settings}));
                    return this;
                },

                rendered: function () {
                    var $actionUnroll = this.$('.action-unenroll'),
                        $unRegisterBlockCourse = this.$('#unregister_block_course'),
                        $actionEmailSettings = this.$('.action-email-settings'),
                        modalType = {
                            unenroll: 'unenroll',
                            emailSettings: 'email-settings'
                        };

                    this.bindModal($actionUnroll, modalType.unenroll);
                    this.bindModal($unRegisterBlockCourse, modalType.unenroll);
                    this.bindModal($actionEmailSettings, modalType.emailSettings);
                },

                bindModal: function ($selector, type) {
                    var trigger,
                        id = _.uniqueId('unenroll-');

                    $selector.leanModal({
                        overlay: 1,
                        closeButton: '.close-modal'
                    });

                    $selector.attr('id', id);
                    trigger = '#' + id;

                    accessibleModal(
                        trigger,
                        _.sprintf('#%(type)s-modal .close-modal', {type: type}),
                        _.sprintf('#%(type)s-modal', {type: type}),
                        '#dashboard-main'
                    );
                },

                toggleCourseActionsDropDown: function (e) {
                    // Suppress the actual click event from the browser
                    e.preventDefault();

                    var ariaExpandedState,
                        $currentTarget = this.$(e.currentTarget),
                        // Toggle the visibility control for the selected element and set the focus
                        $dropDown = this.$('div#actions-dropdown');

                    if ($dropDown.hasClass('is-visible')) {
                        $dropDown.attr('tabindex', -1);
                    } else {
                        $dropDown.removeAttr('tabindex');
                    }

                    $dropDown.toggleClass('is-visible');

                    // Inform the ARIA framework that the dropdown has been expanded
                    ariaExpandedState = ($currentTarget.attr('aria-expanded') === 'true');
                    $currentTarget.attr('aria-expanded', !ariaExpandedState);
                },

                unEnroll: function (e) {
                    var $currentTarget = this.$(e.currentTarget),
                        track_info = $currentTarget.data('track-info'),
                        courseId = $currentTarget.data('course-id'),
                        courseNumber = $currentTarget.data('course-number'),
                        courseName = $currentTarget.data('course-name'),
                        certNameLang = $currentTarget.data('cert-name-long'),
                        refundInfo = $currentTarget.data('refund-info');

                    $('#track-info').html(_.sprintf(track_info, {
                        course_number: _.sprintf(
                            "<span id='unenroll_course_number'>%(courseNumber)s</span>", {courseNumber: courseNumber}
                        ),
                        course_name: _.sprintf(
                            "<span id='unenroll_course_name'>%(courseName)s</span>", {courseName: courseName}
                        ),
                        cert_name_long: _.sprintf(
                            "<span id='unenroll_cert_name'>%(certNameLang)s</span>", {certNameLang: certNameLang}
                        )
                    }, true));

                    $('#refund-info').html(refundInfo);
                    $('#unenroll_course_id').val(courseId);
                },

                emailSettings: function (e) {
                    var $currentTarget = this.$(e.currentTarget);

                    $('#email_settings_course_id').val($currentTarget.data('course-id'));
                    $('#email_settings_course_number').text($currentTarget.data('course-number'));

                    if ($currentTarget.data('optout') === 'False') {
                        $('#receive_emails').prop('checked', true);
                    }
                },

                upgradeToVerified: function (e) {
                    var $currentTarget = this.$(e.currentTarget);
                    $currentTarget.closest('.action-upgrade').data('user');
                    $currentTarget.closest('.action-upgrade').data('course-id');
                },

                unRegisterBlockCourse: function (e) {
                    var $currentTarget = this.$(e.currentTarget),
                        courseId = $currentTarget.data('course-id'),
                        courseNumber = $currentTarget.data('course-number'),
                        courseName = $currentTarget.data('course-name');

                    if (this.$('#block-course-msg').length) {
                        $('.disable-look-unregister').click();
                    }

                    $('#track-info').html(_.sprintf(
                        "<span id='unenroll_course_number'>%(courseNumber)s</span> " +
                        "- <span id='unenroll_course_name'>%(courseName)s?</span>",
                        {courseNumber: courseNumber, courseName: courseName})
                    );

                    $('#unenroll_course_id').val(courseId);
                }
            });

            return CourseView;
        });

}).call(this, define || RequireJS.define, accessible_modal); // jshint undef:false
