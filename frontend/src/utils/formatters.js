// src/utils/formatters.js
import jMoment from 'moment-jalaali';

jMoment.loadPersian({ usePersianDigits: true, dialect: 'fa' });

const isoDateRegex = /^\d{4}-\d{2}-\d{2}/;

/**
 * تبدیل اعداد فارسی به انگلیسی
 * مثال: "۱۴۰۲" -> "1402"
 */
export function toEnglishDigits(str) {
  if (!str) return str;
  return String(str).replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d));
}

/**
 * تاریخ میلادی (ISO) را به تاریخ شمسی (jYYYY/jMM/jDD) تبدیل می‌کند.
 */
export function formatJalaliDate(isoString) {
  if (!isoString || !isoDateRegex.test(isoString)) {
    return isoString;
  }
  try {
    return jMoment(isoString).format('jYYYY/jMM/jDD');
  } catch (e) {
    return isoString;
  }
}

/**
 * تاریخ و زمان میلادی (ISO) را به شمسی (jYYYY/jMM/jDD HH:mm) تبدیل می‌کند.
 */
export function formatJalaliDateTime(isoString) {
  if (!isoString || !isoDateRegex.test(isoString)) {
    return isoString;
  }
  try {
    return jMoment(isoString).format('jYYYY/jMM/jDD HH:mm');
  } catch (e) {
    return isoString;
  }
}