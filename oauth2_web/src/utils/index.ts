// Copyright (c) Huawei Technologies Co., Ltd. 2023-2024. All rights reserved.
// licensed under the Mulan PSL v2.
// You can use this software according to the terms and conditions of the Mulan PSL v2.
// You may obtain a copy of Mulan PSL v2 at:
//      http://license.coscl.org.cn/MulanPSL2
// THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
// PURPOSE.
// See the Mulan PSL v2 for more details.

/**
 * Creates a deep copy of the provided array or object.
 *
 * @param {Array<any>} arr - The array or object to be cloned.
 * @return {Array<any> | Object} The cloned array or object.
 */
export function deepClone(arr: Array<any>): Array<any> | Object {
  const clone = Array.isArray(arr) ? [] : {}
  for (const item in arr) {
    if (Object.prototype.hasOwnProperty.call(arr, item)) {
      if (typeof arr[item] === 'object' && arr[item] !== null)
        clone[item] = deepClone(arr[item])
      else
        clone[item] = arr[item]
    }
  }
  return clone
}

/**
 * Checks if there is any intersection between two arrays.
 *
 * @param {string[]} arr1 - The first array.
 * @param {string[]} arr2 - The second array.
 * @return {boolean} Returns true if there is any intersection, false otherwise.
 */
export function hasIntersection(arr1: string[], arr2: string[]): boolean {
  const set1 = new Set(arr1)
  for (const item of arr2) {
    if (set1.has(item))
      return true
  }
  return false
}

/**
 * Checks if a given value is either an array or an object.
 *
 * @param {any} value - The value to be checked.
 * @return {boolean} Returns true if the value is an array or an object, false otherwise.
 */
export function isArrayOrObject(value: any): boolean {
  if (Array.isArray(value))
    return true

  if (typeof value === 'object' && value !== null)
    return true

  return false
}

/**
 * Checks if a given value is an object.
 *
 * @param {*} value - the value to be checked
 * @return {boolean} true if the value is an object, false otherwise
 */
export function isObject(value: any): boolean {
  return !!(typeof value === 'object' && value !== null)
}


/**
 * Checks if two objects are deeply equal.
 *
 * @param {object} obj1 - The first object to compare.
 * @param {object} obj2 - The second object to compare.
 * @return {boolean} Returns true if the objects are deeply equal, false otherwise.
 */
export function isDeepEqual(obj1: object, obj2: object): boolean {
  // same references
  if (obj1 === obj2) return true;

  if (typeof obj1 !== 'object' || obj1 === null ||
    typeof obj2 !== 'object' || obj2 === null) {
    return false;
  }
  const obj1Keys = Object.keys(obj1);
  const obj2Keys = Object.keys(obj2);

  if (obj1Keys.length !== obj2Keys.length) return false;

  for (let key of obj1Keys) {
    if (!obj2Keys.includes(key) || !isDeepEqual(obj1[key], obj2[key])) {
      return false;
    }
  }

  return true;
}

